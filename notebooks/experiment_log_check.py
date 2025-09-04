import os
import glob
import pandas as pd


def main(folder="view100"):
    base_dir = f"../{folder}"  # view100 experiments   change if needed

    records = []

    if folder == "view100":
        pattern = os.path.join(base_dir, "*", "*", "*", "*", "*1_agents_part_0.csv")
    else:
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
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(str(e))
            print(filepath)
            return 0

        df["dataset"] = dataset
        df["noise"] = dataset_noise
        df["model"] = model
        df["agent_num"] = agent_num

        records.append(df[["dataset", "noise", "model", "agent_num"]])

    df = pd.concat(records, ignore_index=True)
    aggregated_df = (
        # df.groupby(["dataset", "noise", "model", "agent_num"])
        df.groupby(["dataset", "noise", "model", "agent_num"])
        .size()
        .reset_index(name="count")
    )
    print(df.head(5))
    print(aggregated_df.head(5))

    aggregated_df.to_csv(f"aggregated_df_{folder}.csv")


if __name__ == "__main__":
    # view100 experiments   change if needed
    main(folder="view100")
    main(folder="experiments")
