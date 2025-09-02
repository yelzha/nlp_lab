import os
import glob
import pandas as pd

def main():
    base_dir = "../view100"  # change if needed

    records = []

    # Loop over all .txt files in the nested folder structure
    pattern = os.path.join(base_dir, "*", "*", "*", "*", "merged_record.csv")
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

        # with open(filepath, "r", encoding="utf-8") as f:
        #     text = f.read()
        df = pd.read_csv(filepath)

        df["dataset"] = dataset
        df["noise"] = dataset_noise
        df["model"] = model
        df["agent_num"] = agent_num

        records.append(df)

    df = pd.concat(records, ignore_index=True)
    aggregated_df = (
        # df.groupby(["dataset", "noise", "model", "agent_num"])
        df.groupby(["dataset", "noise", "model", "agent_num"])
        .size()
        .reset_index(name="count")
    )
    print(df.head(5))
    print(aggregated_df.head(5))

    aggregated_df.to_csv("aggregated_df.csv")


if __name__ == "__main__":
    main()
