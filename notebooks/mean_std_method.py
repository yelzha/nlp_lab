import glob
import os
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math
from scipy.interpolate import make_interp_spline

from AgentForestRefactored.src.math_equivalence import *


def get_majority_voting_answer(agent_answers):
    counter = Counter(agent_answers)
    majority_voting_answer = counter.most_common(1)[0][0]
    return majority_voting_answer


def get_majority_voting_answer_for_math(agent_answers):
    count = len(agent_answers)
    sameAsCount = [0 for i in range(count)]
    for i in range(count):
        j = i + 1
        while j < count:
            if is_equiv(agent_answers[i], agent_answers[j]):
                sameAsCount[i] += 1
                sameAsCount[j] += 1
            j += 1
    largestCount = 0
    for i in range(count):
        if sameAsCount[i] > sameAsCount[largestCount]:
            largestCount = i
    return agent_answers[largestCount]


def get_majority_voting_answer_for_gsm(agent_answers):
    def most_frequent(List):
        counter = 0
        num = List[0]

        for i in List:
            current_frequency = List.count(i)
            if current_frequency > counter:
                counter = current_frequency
                num = i
        return num

    pred_answer = most_frequent(agent_answers)
    try:
        if pred_answer is None:
            return math.nan

        if len(pred_answer) == 0:
            return math.nan
        pred_answer = float(pred_answer)
        return pred_answer
    except:
        return math.nan



def plot_grid_models_by_noise(df: pd.DataFrame, save_path: Path = None):
    """
    4x6 grid:
        - Rows: dataset
        - Cols: noise
        - Lines: models (accuracy vs agent_num)
    """
    datasets = sorted(df["dataset"].unique())
    noises = sorted(df["noise"].unique())

    # Create consistent order for models
    model_order = sorted(df["model"].unique())

    fig, axes = plt.subplots(len(datasets), len(noises), figsize=(18, 12), sharey=True)

    for i, dataset in enumerate(datasets):
        for j, noise in enumerate(noises):
            ax = axes[i, j]
            sub = df[(df["dataset"] == dataset) & (df["noise"] == noise)]

            for model in model_order:
                g = sub[sub["model"] == model].sort_values("agent_num")
                if g.empty:
                    continue
                ax.plot(g["agent_num"], g["accuracy"], marker="o", label=model)

            if i == 0:
                ax.set_title(noise, fontsize=11)
            if j == 0:
                ax.set_ylabel(dataset.upper())
            ax.set_xlabel("Agent Num")
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(fontsize=8)

    fig.suptitle("Accuracy by Agent Num — Rows: Dataset, Cols: Noise, Labels: Models", y=1.02, fontsize=14)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=200)
    plt.show()


def plot_layered_volume(data_dict):
    """
    Generates a plot with a layered volume to visualize data distribution.

    Args:
        data_dict (dict): A dictionary where keys are x-points and values
                          are numpy arrays of y-data.
    """
    # Get a sorted list of the x-points from the provided dictionary
    x_points = sorted(data_dict.keys())

    # Calculate the mean of each batch of y-data.
    means = [np.mean(data_dict[x]) for x in x_points]

    # Define the percentile levels and corresponding darkness (alpha) values for the layers.
    # The innermost layer will be the darkest.
    percentile_levels = [
        (40, 60),  # Innermost layer, around the median
        (30, 70),
        (20, 80),
        (10, 90),
    ]
    alphas = [0.3, 0.2, 0.1, 0.05]

    # --- 2. Create the plot ---
    # Set up the plot figure and axes
    plt.figure(figsize=(10, 6))
    plt.style.use('seaborn-v0_8-whitegrid')

    # Plot the multi-layered volume dynamically
    for (lower_p, upper_p), alpha in zip(percentile_levels, alphas):
        # Calculate the percentile boundaries for each y-data set
        y_lower_points = [np.percentile(data_dict[x], lower_p) for x in x_points]
        y_upper_points = [np.percentile(data_dict[x], upper_p) for x in x_points]

        # Create smooth curved lines using splines
        x_curve = np.linspace(min(x_points), max(x_points), 200)

        # Use a spline degree of 3 for a smooth curve.
        # This requires at least 4 data points.
        if len(x_points) >= 4:
            spline_lower = make_interp_spline(x_points, y_lower_points, k=3)
            y_lower_curve = spline_lower(x_curve)

            spline_upper = make_interp_spline(x_points, y_upper_points, k=3)
            y_upper_curve = spline_upper(x_curve)

            # Fill the area between the curved lines
            plt.fill_between(
                x_curve,
                y_lower_curve,
                y_upper_curve,
                color='green',
                alpha=alpha,
            )
        else:
            # Fall back to a linear spline if there are not enough points
            spline_lower = make_interp_spline(x_points, y_lower_points, k=1)
            y_lower_curve = spline_lower(x_curve)

            spline_upper = make_interp_spline(x_points, y_upper_points, k=1)
            y_upper_curve = spline_upper(x_curve)

            plt.fill_between(
                x_curve,
                y_lower_curve,
                y_upper_curve,
                color='green',
                alpha=alpha,
            )


    # Plot a dashed line connecting the mean points

    # --- 3. Add labels, title, and a legend ---
    plt.title('Distribution of Y-Points with Layered Volume')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.xticks(x_points)  # Set x-ticks to be exactly at the data points
    plt.legend()
    plt.grid(True)
    plt.xlim(min(x_points) - 1, max(x_points) + 1)  # Adjust the x-axis limits
    plt.ylim(0.0, 1.0)  # Adjust the y-axis limits to focus on the data

    # --- 4. Display the plot ---
    plt.show()


def main():
    # Define the pattern to find the CSV files
    # experiments\clean\gemma-3-4b-it\gsm\log_gsm_clean_20_agents
    base_dir = "../experiments"
    csv_pattern = os.path.join(base_dir, "*", "*", "*", "*_25_agents", "merged_record.csv")
    file_paths = glob.glob(csv_pattern)

    if not file_paths:
        print(f"No files found matching the pattern: {csv_pattern}")
        return

    # Load and combine all the dataframes

    k_values = [1, 5, 10, 15, 20, 25]
    total_agents = 25

    dataframe_k = {}
    all_data_frames = []
    for path in file_paths:
        try:
            df = pd.read_csv(path)
            parts = path.split(os.sep)
            # Extract folder names: {dataset_noise}/{model}/{dataset}/{agent_num}
            noise = parts[-5]
            model_name = parts[-4]
            dataset = parts[-3]
            agent_num_name = parts[-2]
            agent_num = int(agent_num_name.split("_")[-2])

            print(dataset, noise, model_name)
            new_df = pd.DataFrame()
            new_df['dataset'] = dataset
            new_df['noise'] = noise
            new_df['model'] = model_name

            for k in k_values:
                num_groups = total_agents - k + 1
                k_accuracies = []
                for i in range(num_groups):
                    k_group_accuracies = []
                    group_cols = [f"answers_{d}" for d in range(i, i + k)]
                    for index, row in df.iterrows():
                        agent_answers = [row[col] for col in group_cols]
                        if dataset in ("gsm", "multiarith"):
                            voted_answer = get_majority_voting_answer_for_gsm(agent_answers)
                        elif dataset == "math":
                            voted_answer = get_majority_voting_answer_for_math(agent_answers)
                        elif dataset == "mmlu":
                            voted_answer = get_majority_voting_answer(agent_answers)
                        ground_truth = row['ground_truth']
                        is_correct = 1 if voted_answer == ground_truth else 0

                        k_group_accuracies.append(is_correct)

                    k_accuracies.append(np.mean(k_group_accuracies))

                new_df[f"k"] = k
                new_df[f"k_accuracies"] = np.array(k_accuracies)
                all_data_frames.append(new_df)
        except Exception as e:
            print(f"Error reading {path}: {e}")

    if not all_data_frames:
        print("No valid data frames were loaded.")
        return

    combined_df = pd.concat(all_data_frames, ignore_index=True)
    # TODO: finish plotting


if __name__ == "__main__":
    main()