import math
import re
import time
from human_eval.data import read_problems
from human_eval.execution import TimeoutException, create_tempdir, reliability_guard, swallow_io, time_limit
import multiprocessing
from typing import Dict
from collections import Counter
from sacrebleu import sentence_bleu
from math_equivalence import is_equiv
from vllm import LLM, SamplingParams


def get_vllm_name():
    import os
    model_name = os.getenv('VLLM_MODEL_NAME')
    return model_name


VLLM_MODEL_NAME = get_vllm_name()
try:
    global_llm_model = LLM(
        model=VLLM_MODEL_NAME,
        # dtype="float16",
        # gpu_memory_utilization=0.95,
        enforce_eager=False,
    )
    print(f"vLLM model '{VLLM_MODEL_NAME}' initialized globally.")
except Exception as e:
    print(f"Error initializing global vLLM model: {e}")
    global_llm_model = None # Handle case where vLLM fails to initialize


def get_mmlu_qa_pairs(df, ix):
    question = df.iloc[ix, 0]
    a = df.iloc[ix, 1]
    b = df.iloc[ix, 2]
    c = df.iloc[ix, 3]
    d = df.iloc[ix, 4]
    question = "Can you answer the following question as accurately as possible? {}: A) {}, B) {}, C) {}, D) {} Explain your answer, putting the answer in the form (X) at the end of your response.".format(
        question, a, b, c, d)
    answer = df.iloc[ix, 5]
    return question, answer

def get_human_eval_qa_pairs():
    problems = read_problems()
    problems = [(k, v["prompt"], v["entry_point"]) for k, v in problems.items()]
    return problems

def check_function_result(python_code: str, timeout: float = 5.0) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    suite provided in the problem. 

    :param completion_id: an optional completion ID so we can match
        the results later even if execution finishes asynchronously.
    """

    def unsafe_execute():

        with create_tempdir():

            # These system calls are needed when cleaning up tempdir.
            import os
            import shutil
            rmtree = shutil.rmtree
            rmdir = os.rmdir
            chdir = os.chdir

            # Disable functionalities that can make destructive changes to the test.
            reliability_guard()

            # Construct the check program and run it.
            check_program = python_code + "\n"

            try:
                exec_globals = {}
                with swallow_io():
                    with time_limit(timeout):
                        exec(check_program, exec_globals)
                result.append("passed")
            except TimeoutException:
                result.append("timed out")
            except BaseException as e:
                result.append(f"failed: {e}")

            # Needed for cleaning up.
            shutil.rmtree = rmtree
            os.rmdir = rmdir
            os.chdir = chdir

    manager = multiprocessing.Manager()
    result = manager.list()

    p = multiprocessing.Process(target=unsafe_execute)
    p.start()
    p.join(timeout=timeout + 1)
    if p.is_alive():
        p.kill()

    if not result:
        result.append("timed out")

    return dict(
        passed=result[0] == "passed",
        result=result[0],
    )

def batch_generate(answer_context, model, llm_ip=None, nums=1, temperature=1, top_p=1, use_json=False):
    global global_llm_model
    global VLLM_MODEL_NAME
    completion = []
    try:
        # vLLM expects a list of prompts. Your 'answer_context' is a list of message objects.
        # We need to extract the prompt string for each context.
        # If using a chat model, it's best to apply the chat template.

        # This handles your original `contexts` which seems to be a list of message lists
        # e.g., [[{'role': 'user', 'content': 'prompt1'}], [{'role': 'user', 'content': 'prompt2'}]]
        # We'll flatten it to a list of single prompts.
        start = time.time()
        prompts = []
        for ctx in answer_context:
            # Assuming `ctx` is like `[{'role': 'user', 'content': 'Your question here'}]`
            # For more complex chat templates, you'd use global_tokenizer.apply_chat_template(ctx, tokenize=False)
            # For simplicity, assuming a single user message.
            if isinstance(ctx, list) and len(ctx) > 0 and 'content' in ctx[0]:
                prompts.append(ctx[0]['content'])
            else:
                # Handle cases where context might be just a string prompt, if applicable
                prompts.append(str(ctx))  # Fallback, adjust as needed

        if not prompts:
            return []  # No prompts to generate

        # vLLM SamplingParams
        # `n` directly controls how many completions per prompt.
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            n=nums,
            max_tokens=2048
        )

        # Generate completions using vLLM
        outputs = global_llm_model.generate(prompts, sampling_params)

        # Convert vLLM outputs to OpenAI-like format
        for i, output in enumerate(outputs):
            prompt_text = output.prompt  # Or prompts[i]
            prompt_tokens = len(output.prompt_token_ids)

            # Each RequestOutput can have multiple CompletionOutput if n > 1
            choices = []
            total_completion_tokens_for_output = 0
            for completion_output in output.outputs:
                choices.append({
                    "message": {"content": completion_output.text},
                    "finish_reason": completion_output.finish_reason,  # "stop", "length" etc.
                    # You might add logprobs if needed, though not directly available like OpenAI's.
                })
                total_completion_tokens_for_output += len(completion_output.token_ids)

            completion.append({
                "choices": choices,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": total_completion_tokens_for_output,
                    "total_tokens": prompt_tokens + total_completion_tokens_for_output
                },
                "model": VLLM_MODEL_NAME,  # Indicate the model used
                "id": output.request_id  # Unique ID for the request
            })
        print("++++++++++++++++++Time:", time.time() - start, "++++++++++++++++++")

    except Exception as e:
        print(e, flush=True)
        print("retrying due to an error......", flush=True)
        time.sleep(5)
        return batch_generate(answer_context, model, llm_ip,nums=nums,temperature=temperature,top_p=top_p)
    return completion

def extract_last_python_code_block(text):
    # The regular expression pattern for Python code blocks
    pattern = r"```[pP]ython(.*?)```"

    # Find all matches in the text
    matches = re.findall(pattern, text, re.DOTALL)

    # If there are matches, return the last one
    if matches:
        return matches[-1].strip()
    else:
        return None

def parse_code_completion(agent_response, question):
    python_code = extract_last_python_code_block(agent_response)
    if python_code is None:
        if agent_response.count("impl]") == 0:
            python_code = agent_response
        else:
            python_code_lines = agent_response.split("\n")
            python_code = ""
            in_func = False
            for line in python_code_lines:
                if in_func:
                    python_code += line + "\n"
                if "impl]" in line:
                    in_func = True
    if python_code.count("def") == 0:
        python_code = question + python_code
    return python_code, True

def most_frequent(clist, cmp_func):
    counter = 0
    num = clist[0]

    for i in clist:
        current_frequency = sum(cmp_func(i, item) for item in clist)
        print("current_frequency", current_frequency)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num, counter

def get_majority_voting_answer(agent_answers):
    counter = Counter(agent_answers)
    majority_voting_answer = counter.most_common(1)[0][0]
    return majority_voting_answer

def get_majority_voting_answer_for_gsm(agent_answers):
    def most_frequent(List):
        counter = 0
        num = List[0]

        for i in List:
            current_frequency = List.count(i)
            if current_frequency > counter:
                counter = current_frequency
                num = i

        return num
    pred_answer = most_frequent(agent_answers)
    if len(pred_answer) == 0:
        return math.nan
    try:
        pred_answer = float(pred_answer)
        return pred_answer
    except:
        return math.nan

def get_majority_voting_answer_for_math(agent_answers):
    count = len(agent_answers)
    sameAsCount = [0 for i in range(count)]
    for i in range(count):
        j = i + 1
        while j < count:
            if is_equiv(agent_answers[i], agent_answers[j]):
                sameAsCount[i] += 1
                sameAsCount[j] += 1
            j += 1
    largestCount = 0
    for i in range(count):
        if sameAsCount[i] > sameAsCount[largestCount]:
            largestCount = i
    return agent_answers[largestCount]

def most_similar_code(clist):
    cmp_res = lambda x, y: sentence_bleu(x, [y], lowercase=True).score
    if len(clist) == 1:
        return 0, clist[0], 0
    bleu_scores = []
    for idx, agent in enumerate(clist):
        total_score = 0
        for idx_o, otheragent in enumerate(clist):
            if idx == idx_o:
                continue
            total_score += cmp_res(agent, otheragent)
        bleu_scores.append(total_score)
    max_index, max_value = max(enumerate(bleu_scores), key=lambda x: x[1])
    return max_index, clist[max_index], max_value

def mmlu_ans_parser(answer_text, question=None):
    finalIndex = answer_text.find("Final answer:")
    if finalIndex > 0:
        answer_text = answer_text[finalIndex:]
    pattern = r'\((\w)\)'
    matches = re.findall(pattern, answer_text)
    if len(matches) == 0:
        matches = re.findall(r'(\w)\)', answer_text)
        if len(matches) == 0:
            matches = re.findall(r' ([A-Z]) ', answer_text)
    answer = None
    for match_str in matches[::-1]:
        answer = match_str.upper()
        if answer:
            break
    return answer, True

def math_ans_parser(answer_text, question=None):
    # Find all occurrences of the \boxed{} pattern and extract the content, accounting for nested braces
    # matches = re.findall(r'\\boxed{((?:[^{}]*|{[^{}]*})*)}', answer_text)
    #
    # # Return the content of the last occurrence, or None if there were no matches
    # if matches:
    #     return matches[-1], True
    # return None, False

    match = re.search(r'\\boxed{(.*)}', answer_text)
    if match:
        return match.group(1),True
    else:
        return None , False
    # return match.group(1), True if match else None,False

def gsm_ans_parser(answer_text, question=None):
    def parse_answer(input_str):
        pattern = r"\{([0-9.,$]*)\}"
        matches = re.findall(pattern, input_str)

        solution = None

        for match_str in matches[::-1]:
            solution = re.sub(r"[^0-9.]", "", match_str)
            if solution:
                break

        return solution

    def solve_math_problems(input_str):
        pattern = r"\d+\.?\d*"

        matches = re.findall(pattern, input_str)
        if matches:
            return matches[-1]

        return None

    pred_answer = parse_answer(answer_text)

    if pred_answer is None:
        pred_answer = solve_math_problems(answer_text)

    return pred_answer, pred_answer is not None

def chess_ans_parser(answer_text, question=None):
    none_responese = [
        "i am unable to provide a valid destination square based on the given chess game and moves",
        "none",
        "no valid",
        "no specific valid",
        "invalid",
        "n/a",
        "unable to provide",
        "game sequence contains errors",
        "i cannot provide"
    ]
    content = answer_text.lower()
    pattern = r"[a-h][1-8]"
    pos = content.rfind("final answer")
    if pos != -1:
        item = content.split("final answer")[-1].strip()
        matches = re.findall(pattern, item)
        if len(matches) == 1:
            return matches[0].lower(), True
        elif len(matches) > 1:
            print([content])
            print("*" * 100)
            return matches[-1].lower(), True
        else:
            for valid_case in none_responese:
                if valid_case in content:
                    return None, False
            return None, False
    else:
        matches = re.findall(pattern, content)
        if len(matches) == 0:
            for valid_case in none_responese:
                if valid_case in content:
                    return None, False
            return None, False
        else:
            return matches[-1], True

def is_final_answer_correct(df_row):
    if df_row["ground_truth"] == df_row["final_answer"]:
        return True
    return False

def is_final_answer_in_ground_truth(df_row):
    if df_row["final_answer"] in df_row["ground_truth"]:
        return True
    return False
