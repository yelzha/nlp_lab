interaction_prompt = {
    "mmlu": {
        "question": "Can you answer the following question as accurately as possible? Question: {}: \n Choices: A) {}, B) {}, C) {}, D) {}. Briefly explain your reasoning. At the end, output only one final answer like \\boxed{{(A)}}, \\boxed{{(B)}}, \\boxed{{(C)}}, or \\boxed{{(D)}}.",
        "debate": [
            "These are the solutions to the problem from other agents:\n\n{other_agents}\n",
            "Using the reasoning from other agents as additional input, re-evaluate your own answer step by step. Choose only one of A, B, C, or D. End your updated response on a new line in the format: (A), (B), (C), or (D). Do not add extra commentary after the answer."
        ],
        "reflection": "Now carefully reflect on your most recent answer. Ensure it is logically consistent, factually accurate, and best supported by the reasoning. If you believe a different choice is better, update it. End with your final answer on a new line in the format: (A), (B), (C), or (D), and do not write anything else after that."
    },
    "math":{
        "question": "Here is a math problem written in LaTeX:{}\n Explain your reasoning briefly. Put your answer in the form \\boxed{{answer}}, at the end of your response.",
        "debate": [
            "These are the solutions to the problem from other agents:",
            "\n\nUsing the reasoning from other agents as additional information and referring to your historical answers, can you give an updated answer? Put your answer in the form \\boxed{{answer}}, at the end of your response."
        ],
        "reflection": "Can you double check that your answer is correct? Please reiterate your answer, with your answer in the form \\boxed{{answer}}, at the end of your response.",
    },
    "chess":{
        "question": "Given the chess game \"{}\", give one valid destination square for the chess piece at \"{}\". Give a one line explanation of why your destination square is a valid move. State your final answer in a newline with a 2 letter response following the regex [a-h][1-8]. ",
        "debate": [
            "Here are destination square suggestions from other agents:",
            "\n\nCan you double check that your destination square is a valid move? Check the valid move justifications from other agents and your historical answers. State your final answer in a newline with a 2 letter response following the regex [a-h][1-8]."
        ],
        "reflection": "Can you double check that your destination square is a valid move? Check the valid move justifications from your historical answers. State your final answer in a newline with a 2 letter response following the regex [a-h][1-8].",
    },
    "gsm":{
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
