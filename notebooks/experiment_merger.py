import os
import glob
import pandas as pd

def main():
    base_dir = "../experiments"  # change if needed

    records = []

    # Loop over all .txt files in the nested folder structure
    pattern = os.path.join(base_dir, "*", "*", "*", "*", "*.txt")
    for filepath in glob.glob(pattern):
        parts = filepath.split(os.sep)
        # Extract folder names: {dataset_noise}/{model}/{dataset}/{agent_num}
        dataset_noise = parts[-5]
        model = parts[-4]
        dataset = parts[-3]
        agent_num_name = parts[-2]
        agent_num = int(agent_num_name.split("_")[-2])

        if agent_num > 25:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Example: extract all floating numbers from file
        import re

        values = re.findall(r"[-+]?\d*\.\d+|\d+", text)  # matches ints and floats

        records.append({
            "model": model,
            "dataset": dataset,
            "noise": dataset_noise,
            "agent_num": agent_num,
            "accuracy": values[0]
        })

    df = pd.DataFrame(records)
    df = df.sort_values(["model", "dataset", "noise", "agent_num"])
    print(df.head(5))

    # Optional: save to CSV
    df.to_csv("merged_results.csv", index=False)


if __name__ == "__main__":
    main()
