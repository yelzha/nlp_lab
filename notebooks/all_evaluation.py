import os
import glob
import pandas as pd
from AgentForestRefactored.src import evaluation

def main(folder="experiments"):
    base_dir = f"../{folder}"  # change if needed

    records = []

    # Loop over all .txt files in the nested folder structure
    pattern = os.path.join(base_dir, "*", "*", "*", "*")
    for filepath in glob.glob(pattern):
        if ".txt" in filepath:
            continue
        print(filepath)
        parts = filepath.split(os.sep)
        # Extract folder names: {dataset_noise}/{model}/{dataset}/{agent_num}
        dataset = parts[-2]
        dataset_noise = parts[-4]
        model = parts[-3]
        agent_num_name = parts[-1]
        agent_num = int(agent_num_name.split("_")[-2])

        print(dataset, dataset_noise, model, agent_num)
        evaluation.merge_record(filepath)
        evaluation.evaluation(filepath)


if __name__ == "__main__":
    main("experiments")
    print("Done!")
