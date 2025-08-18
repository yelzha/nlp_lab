interaction_prompt = {
    "mmlu": {
        "question": "Can you answer the following question as accurately as possible? Question: {}: \n Choices: A) {}, B) {}, C) {}, D) {}. Briefly explain your reasoning. Choose only one of A, B, C, or D. At the end, output only one final answer like \\boxed{{(A)}}, \\boxed{{(B)}}, \\boxed{{(C)}}, or \\boxed{{(D)}}. Do not add extra commentary after the answer. Do not include anything else on that final line.",
    },
    "math": {
        "question": "Here is a math problem written in LaTeX: {}\n\nSolve it step by step. \n- If the correct answer has units, write the units OUTSIDE the box in plain text. \n- Inside \\boxed{{...}} put only the simplest exact numeric expression (no units), fully simplified \n(e.g., rationalized denominator, reduced fractions, simplified radicals). \nAt the very end of your response, output exactly one line: \\boxed{<simplest_exact_value>} \nIf units are required, add a space and then the units in words after the box, e.g.: \boxed{{8.5}} square inches \n Do not add any extra commentary after that line.",
    },
    "gsm": {
        "question" : "Can you solve the following math problem? {} Explain your reasoning. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response. "
    },
    "multiarith":{
        "question" : "Can you solve the following math problem? {} Explain your reasoning. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response. "
    }
}


def construct_message(question, qtype):
    if qtype == "code_completion":
        qtemplate = "```python\n{}\n```"
        qtemplate = '''You must complete the python function I give you.
        Be sure to use the same indentation I specified. Furthermore, you may only write your response in code/comments.
        [function impl]:
        {}\nOnce more, please follow the template by repeating the original function, then writing the completion.'''\
            .format(qtemplate.format(question))
        return {"role": "user", "content": qtemplate}
    elif qtype == "mmlu":
        return {"role": "user", "content": question}
    elif qtype == "math":
        return {"role": "user", "content": question}
    elif qtype == "chess":
        return {"role": "user", "content": question}
    elif qtype == "gsm":
        return {"role": "user", "content": question}
    elif qtype == "multiarith":
        return {"role": "user", "content": question}
    elif qtype == "istask":
        return {"role": "user", "content": question}
    elif qtype == "sstask":
        return {"role": "user", "content": question}
    else:
        return {"role": "user", "content": question}
