from glob import glob

import pandas as pd

import categories
from AgentForestRefactored.src.prompt_lib import interaction_prompt


def windows_to_linux_path(windows_path):
    # 替换反斜杠为正斜杠
    linux_path = windows_path.replace('\\', '/')
    # 如果存在Windows驱动器字母，去除冒号
    if ':' in linux_path:
        linux_path = linux_path.replace(':', '')
    return linux_path

def get_mmlu_qa_pairs(df, ix):
    question = df.iloc[ix, 0]
    a = df.iloc[ix, 1]
    b = df.iloc[ix, 2]
    c = df.iloc[ix, 3]
    d = df.iloc[ix, 4]
    answer = df.iloc[ix, 5]
    question = interaction_prompt["mmlu"]["question"].format(
        question, a, b, c, d)
    return question, answer

def get_question_datas():
    math_files = [
        'abstract_algebra_test.csv',
        'college_mathematics_test.csv',
        'elementary_mathematics_test.csv',
        'high_school_mathematics_test.csv',
        'high_school_statistics_test.csv'
    ]
    tasks = glob(f"../dataset/mmlu/mmlu_dataset_clean/*.csv")
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
    dfs = [
        pd.read_csv(task) for task in tasks
        if windows_to_linux_path(task).split("/")[-1] in math_files
    ]

    names = [
        task for task in tasks
        if windows_to_linux_path(task).split("/")[-1] in math_files
    ]

    print(names)
    print([i.shape[0] for i in dfs])
    print(sum([i.shape[0] for i in dfs]))

    question_datas = []
    for df in dfs:
        ix = len(df)
        for idx in range(ix):
            question_state, ground_truth = get_mmlu_qa_pairs(df, idx)
            question_data = {
                "state": question_state,
                "ground_truth": ground_truth,
            }
            question_datas.append(question_data)

    # random.seed(0)
    # random.shuffle(question_datas)
    return question_datas


d = get_question_datas()
print(d[:2])
print(len(d))
