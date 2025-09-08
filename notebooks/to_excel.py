import os
import glob
import pandas as pd


def main(folder="view100"):
    base_dir = f"../{folder}"  # view100 experiments   change if needed

    records = []

    pattern = os.path.join(base_dir, "*", "*", "*", "*_1_agents", "*_agents_part_0.csv")

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

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(str(e))
            print(filepath)
            return 0

        cols = df.columns.tolist()

        df["dataset"] = dataset
        df["noise"] = dataset_noise
        df["model"] = model
        df["agent_num"] = agent_num

        records.append(df[["dataset", "noise", "model", "agent_num"] + cols].iloc[:10, :])

    df = pd.concat(records, ignore_index=True)

    out_path = f"manual_df_{folder}.xlsx"
    # df.to_excel(out_path)
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)


if __name__ == "__main__":
    # view100 experiments   change if needed
    main(folder="view100")
