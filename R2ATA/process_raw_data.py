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

# from glob import glob
# import csv
# import json
#
# path = "data/mmlu"
# tasks = glob(f"{path}/*.csv")
#
# dataset = []
# dataset_len = []
# for task in tasks:
#     with open(task, mode="r", encoding="utf-8") as csvfile:
#         reader = csv.reader(csvfile)
#         cnt = 0
#         chunk = []
#         for row in reader:
#             chunk.append([i for i in row])
#             cnt += 1
#         dataset.append(chunk)
#         dataset_len.append(cnt)
#
#
# path = f"experiments/results/llama_mmlu_0_shots_20250810-131334.json"
#
# with open(path, 'r', encoding='utf8') as file:
#     questions = json.load(file)
#
# question_datas = []
# for i in range(len(dataset_len)):
#     start = sum(dataset_len[:i])
#     end = sum(dataset_len[:i+1])
#     print(start, end)
#     new_set_of_questions = questions['tests'][4::5]
#     raw_dataset = dataset[i]
#     question_chunks = []
#     for q, gt, raw in zip(new_set_of_questions[start:end], questions['correct_answer'], raw_dataset):
#         q_parsed = (
#             list(q.keys())[0]
#             .replace("Question: ", "")
#             .replace("\nAnswer: Let's think step by step.", "")
#             .strip()
#             .split("\n Choices:")[0])
#         # print("***************")
#         # print("Q:", q_parsed)
#         # print("A:", gt)
#         # print("++++++++++++++++++++++")
#         question_chunks.append({
#             0: q_parsed,
#             1: raw[1],
#             2: raw[2],
#             3: raw[3],
#             4: raw[4],
#             5: raw[5]
#         })
#     question_datas.append(question_chunks)
#
# import pandas as pd
#
# mmlu_file_names = [i.split("\\")[-1] for i in tasks]
#
# mmlu = [
#     pd.DataFrame(questions_[:]).to_csv(f"prepared_data/mmlu_dataset_r2ata/{mmlu_name}", index=False)
#     for questions_, mmlu_name in zip(question_datas, mmlu_file_names)
# ]







# import json
#
# path = f"experiments/results/llama_math_0_shots_20250810-131421.json"
#
# with open(path, 'r', encoding='utf8') as file:
#     questions = json.load(file)
#
# question_datas = []
# for q, gt in zip(questions['tests'][4::5], questions['correct_answer']):
#     q_parsed = list(q.keys())[0].replace("Question: ", "").replace("\nAnswer: Let's think step by step.", "").strip()
#     question_datas.append({
#         "question": q_parsed,
#         "answer": gt
#     })
#
# # print(question_datas[:2])
#
# q_iter = iter(question_datas)
# sampledMathSet = json.load(open("data/math.json"))
# for level in sampledMathSet.keys():
#     for category in sampledMathSet[level].keys():
#         for problem in sampledMathSet[level][category]:
#             q = next(q_iter)
#             problem['problem'] = q['question']
#
# print(sampledMathSet)
#
# path = f"prepared_data/math_dataset_r2ata/math_subset_20.json"
# with open(path, 'w', encoding='utf8') as f:
#     json.dump(sampledMathSet, f, ensure_ascii=False, indent=2)



# import json
#
# path = f"experiments/results/llama_multiarith_0_shots_20250810-131630.json"
#
# with open(path, 'r', encoding='utf8') as file:
#     questions = json.load(file)
#
# question_datas = []
# for q, gt in zip(questions['tests'][4::5], questions['correct_answer']):
#     q_parsed = list(q.keys())[0].replace("Question: ", "").replace("\nAnswer: Let's think step by step.", "").strip()
#     question_datas.append({
#         "question": q_parsed,
#         "final_ans": gt
#     })
#
# path = f"prepared_data/multiarith_dataset_r2ata/test.json"
# with open(path, 'w', encoding='utf8') as f:
#     json.dump(question_datas, f, ensure_ascii=False, indent=2)
