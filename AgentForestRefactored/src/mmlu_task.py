import pandas as pd
import random
import utils
import categories
from glob import glob

from prompt_lib import interaction_prompt
from more_agent import MoreAgent

def windows_to_linux_path(windows_path):
    # 替换反斜杠为正斜杠
    linux_path = windows_path.replace('\\', '/')
    # 如果存在Windows驱动器字母，去除冒号
    if ':' in linux_path:
        linux_path = linux_path.replace(':', '')
    return linux_path

class MMLU(MoreAgent):
    def __init__(self, agents_num, model_type, nums=1, temperature=1, top_p=1, dtype="clean"):
        self.qtype = "mmlu"
        self.dtype = dtype
        self.ans_parser = utils.mmlu_ans_parser
        self.format_prompt = ("Explain your answer step by step. "
                              "Then, on a new line, write only your final answer in the format: "
                              "(A), (B), (C), or (D).")
        super().__init__(agents_num, model_type, nums, temperature, top_p)

    def get_question_datas(self, question_num=100):
        tasks = glob("../dataset/mmlu_dataset/*.csv")
        category = {}
        reverseCategory = {}
        resultInCategory = {}
        for key in categories.categories.keys():
            for c in categories.categories[key]:
                reverseCategory[c] = key
            resultInCategory[key] = []
        index = 0
        for task in tasks:
            l_task = windows_to_linux_path(task)
            fileName = l_task.split("/")[-1]
            tail = fileName.rfind("_")
            fileName = fileName[0:tail]
            subCate = categories.subcategories[fileName][0]
            category[index] = reverseCategory[subCate]
            index += 1
        dfs = [pd.read_csv(task) for task in tasks]

        question_datas = []
        for df in dfs:
            ix = len(df)
            for idx in range(ix):
                question_state, ground_truth = utils.get_mmlu_qa_pairs(df, idx)
                question_data = {
                    "state": question_state,
                    "ground_truth": ground_truth,
                }
                question_datas.append(question_data)

        random.seed(0)
        random.shuffle(question_datas)
        return question_datas

    def get_final_answer(self, idxs, question_data):
        agent_answers = [self.nodes[idx].get_answer() for idx in idxs]
        consistent_answer = utils.get_majority_voting_answer(agent_answers)
        return consistent_answer

    def evaluation(self, df):
        return df.apply(utils.is_final_answer_correct, axis=1).mean()


if __name__ == "__main__":
    mmlu = MMLU(1, "test")
    test = mmlu.get_question_datas()
    print(len(test))
    print(test[:50])