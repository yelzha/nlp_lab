# import json
# import os
#
#
# path = f"experiments/results/llama_gsm8k_0_shots_20250809-170631.json"
#
# with open(path, 'r', encoding='utf8') as file:
#     questions = json.load(file)
#
# question_datas = []
# for q, gt in zip(questions['tests'][4::5], questions['correct_answer']):
#     q_parsed = list(q.keys())[0].replace("Question: ", "").replace("\nAnswer: Let's think step by step.", "").strip()
#     # print("***************")
#     # print("Q:", q_parsed)
#     # print("A:", gt)
#     # print("++++++++++++++++++++++")
#     question_datas.append({
#         "question": q_parsed,
#         "answer": gt
#     })
#
# folder_path = "prepared_data/gsm_dataset_r2ata"
# file_path = os.path.join(folder_path, "test.jsonl")
# os.makedirs(folder_path, exist_ok=True)
#
# with open(file_path, "w", encoding="utf-8") as f:
#     for record in question_datas:
#         json_line = json.dumps(record, ensure_ascii=False)
#         f.write(json_line + "\n")
#
# print("Data written to output.jsonl")

from glob import glob
import csv

path = "data/"
tasks = glob(f"{path}/*.csv")

dataset = []
for task in tasks:
    with open(task, mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            question = f"{row[0]} \n Choices: A) {row[1]}, B) {row[2]}, C) {row[3]}, D) {row[4]}"
            dataset.append(question)

print(dataset[:2])
