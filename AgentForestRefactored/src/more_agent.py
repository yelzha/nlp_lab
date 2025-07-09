import ast
import prompt_lib
from agent import Agent
from utils import batch_generate

class MoreAgent():
    def __init__(self, agents_num, model_type, nums=1, temperature=1, top_p=1):
        self.mtype = model_type
        self.agents = agents_num
        self.nums = nums
        self.temperature = temperature
        self.top_p = top_p
        self.init_nn()

    def init_nn(self):
        self.nodes = []
        for _ in range(self.agents):
            self.nodes.append(Agent(self.qtype, self.mtype, self.ans_parser, self.qtype, nums=self.nums, temperature=self.temperature, top_p=self.top_p))

    def forward(self, question_data, batch_size=50):
        """
        Generates responses from all initialized agents in a batch and returns
        their parsed answers for external voting.
        """
        def get_completions_and_answers():
            completions = [[] for _ in range(self.agents)]
            answers = [[] for _ in range(self.agents)]
            return completions, answers
        total_prompt_tokens, total_completion_tokens = 0, 0
        question_state = question_data["state"]

        # Prepare the initial context for each agent.
        # self.nodes[0].preprocess(question_state) returns a list of messages (e.g., system prompt).
        # prompt_lib.construct_message adds the user's question.
        # The resulting `contexts_for_one_agent` is the full prompt for a single agent.
        contexts_for_one_agent = self.nodes[0].preprocess(question_state)
        if not isinstance(contexts_for_one_agent, list):
            contexts_for_one_agent = [contexts_for_one_agent]  # Ensure it's a list
        contexts_for_one_agent.append(prompt_lib.construct_message(question_state, self.nodes[0].qtype))

        # Create a list of identical contexts, one for each agent, to send to batch_generate.
        # This allows all agent responses to be generated in a single batched API call.
        all_agent_contexts_for_batch_generate = [contexts_for_one_agent for _ in range(len(self.nodes))]

        batch_num, remainder = divmod(len(all_agent_contexts_for_batch_generate), batch_size)
        content_list = []  # Stores raw LLM completions (strings)

        # Process in batches to avoid sending too many requests at once if batch_size is small
        # or if the total number of agents is very large.
        for i in range(batch_num):
            batch_agent_contexts = all_agent_contexts_for_batch_generate[i * batch_size: (i + 1) * batch_size]
            # nums=1 here means 1 completion per prompt in the batch, as each agent provides one answer.
            batch_completion = batch_generate(batch_agent_contexts, self.nodes[0].model, self.nodes[0].llm_ip, nums=1)

            # Aggregate token usage and extract content from each completion
            for comp_item in batch_completion:
                total_prompt_tokens += comp_item["usage"]["prompt_tokens"]
                total_completion_tokens += comp_item["usage"]["completion_tokens"]
                for choice in comp_item["choices"]:
                    content_list.append(choice["message"]["content"])

        # Handle any remaining agents that don't fit into a full batch
        if remainder > 0:
            batch_agent_contexts = all_agent_contexts_for_batch_generate[
                                   batch_num * batch_size: (batch_num * batch_size) + remainder]
            batch_completion = batch_generate(batch_agent_contexts, self.nodes[0].model, self.nodes[0].llm_ip, nums=1)

            # Aggregate token usage and extract content
            for comp_item in batch_completion:
                total_prompt_tokens += comp_item["usage"]["prompt_tokens"]
                total_completion_tokens += comp_item["usage"]["completion_tokens"]
                for choice in comp_item["choices"]:
                    content_list.append(choice["message"]["content"])

        # Ensure that we have a completion for every agent
        assert len(content_list) == len(self.nodes), \
            f"Expected {len(self.nodes)} completions, but got {len(content_list)}"

        all_parsed_answers = []
        # Post-process each agent's raw completion to extract the final answer
        for node_idx in range(len(self.nodes)):
            # print(f"{node_idx} th agent process", flush=True)
            self.nodes[node_idx].postprocess(content_list[node_idx], question_state)
            all_parsed_answers.append(self.nodes[node_idx].get_answer())

        # Return all parsed answers and token usage. The final voting logic
        # for different K values will be handled by the calling script (main.py).
        # result_dict = {
        #     "all_parsed_answers": all_parsed_answers,
        #     "total_prompt_tokens": total_prompt_tokens,
        #     "total_completion_tokens": total_completion_tokens,
        # }
        completions, answers = get_completions_and_answers()
        result_dict = {
            "final_answer": None,
            "completions": completions,
            "answers": all_parsed_answers,
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
        }
        return result_dict

    def cut_def_question(self, func_code, question, entry_point):
        def parse_imports(src_code):
            res = []
            for line in src_code.split("\n"):
                if "import" in line:
                    res.append(line)
            res = ["    " + line.strip() for line in res]
            return res
        import_lines = parse_imports(func_code)

        def extract_functions_with_body(source_code):
            # Parse the source code to an AST
            tree = ast.parse(source_code)

            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if the function is nested inside another function
                    # We can determine this by checking the ancestors of the node
                    parents = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                    nesting_level = sum(1 for parent in parents if
                                        parent.lineno <= node.lineno and parent.end_lineno >= node.end_lineno)

                    if nesting_level == 1:  # Only top-level functions
                        start_line = node.lineno - 1
                        end_line = node.end_lineno
                        function_body = source_code.splitlines()[start_line:end_line]
                        functions.append("\n".join(function_body))

            return functions
        try:
            funcs = extract_functions_with_body(func_code)
        except:
            funcs = [func_code]

        def extract_func_def(src_code):
            for line in src_code.split("\n"):
                if "def" in line and entry_point in line:
                    return line
            return ""
        que_func = extract_func_def(question)

        for fiid, func_ins_code in enumerate(funcs):
            if question in func_ins_code:
                func_ins_code = func_ins_code.split(question)[-1]
            elif question.strip() in func_ins_code:
                func_ins_code = func_ins_code.split(question.strip())[-1]
            elif que_func in func_ins_code:
                # remove the line before def
                res_lines = func_ins_code.split("\n")
                func_ins_code = ""
                in_func = False
                for line in res_lines:
                    if in_func:
                        func_ins_code += line + "\n"
                    if "def" in line:
                        in_func = True
            else:
                continue

            other_funcs = []
            for other_func in funcs[:fiid] + funcs[fiid+1:]:
                other_func = other_func.split("\n")
                other_func = other_func[:1] + import_lines + other_func[1:]
                other_func = "\n".join(other_func)
                other_funcs.append(other_func)

            return "\n".join(import_lines) + "\n" + func_ins_code + "\n" + "\n".join(other_funcs)

        res_lines = func_code.split("\n")
        func_code = ""
        in_func = False
        for line in res_lines:
            if in_func:
                func_code += line + "\n"
            if "def" in line:
                in_func = True

        return "\n".join(import_lines) + "\n" + func_code
