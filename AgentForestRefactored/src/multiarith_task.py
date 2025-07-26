import random
import utils
import json
from more_agent import MoreAgent
from prompt_lib import interaction_prompt
import re


class MULTIARITH(MoreAgent):
    def __init__(self, agents_num, model_type, nums=1, temperature=1, top_p=1, dtype="clean"):
        self.qtype = "multiarith"
        self.dtype = dtype
        self.ans_parser = utils.gsm_ans_parser
        self.format_prompt = "Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response."
        super().__init__(agents_num, model_type, nums, temperature, top_p)

    def get_question_datas(self):
        path = f"../dataset/multiarith/multiarith_dataset_{self.dtype}/test.json"

        question_datas = []

        def read_json(path: str):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data

        questions = read_json(path)
        # random.seed(0)
        # random.shuffle(questions)
        # questions = questions[0:100]
        for q in questions:
            question_state = interaction_prompt["gsm"]["question"].format(q['question'])
            gt = q['final_ans']
            if gt is not None:
                gt = float(gt)
            question_data = {
                "state": question_state,
                "ground_truth": gt,
            }
            question_datas.append(question_data)
        return question_datas

    def get_final_answer(self, idxs, question_data):
        agent_answers = [self.nodes[idx].get_answer() for idx in idxs]
        consistent_answer = utils.get_majority_voting_answer_for_gsm(agent_answers)
        return consistent_answer

    def evaluation(self, df):
        return df.apply(utils.is_final_answer_correct, axis=1).mean()



if __name__ == "__main__":
    ma = MULTIARITH(1, "test")
    test = ma.get_question_datas()
    print(len(test))
    print(test[:2])