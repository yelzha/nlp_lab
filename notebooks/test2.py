# This script loads experimental data from a specific directory structure,
# calculates accuracies for different agent counts, and plots the results
# in a 4x6 grid. Each plot visualizes the accuracy distribution with a
# multi-layered, curved volume and a dashed line for the mean.

import glob
import os
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math
import ast
from scipy.interpolate import make_interp_spline

from AgentForestRefactored.src.math_equivalence import *

# --- Utility functions from user's code ---

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

        pred_answer = float(pred_answer)
        return pred_answer
    except:
        return math.nan


# --- Plotting function (adapted for subplots) ---

def plot_layered_volume(ax, data_dict, color, label):
    """
    Generates a plot with a layered volume to visualize data distribution on a given axis.

    Args:
        ax (matplotlib.axes.Axes): The axes object to plot on.
        data_dict (dict): A dictionary where keys are x-points and values
                          are numpy arrays of y-data.
        color (str): The color for the volume and mean line.
        label (str): The label for the legend.
    """
    x_points = sorted(data_dict.keys())
    if len(x_points) < 2:
        # Cannot plot volume with less than two points. Plot a single point instead.
        if x_points:
            ax.plot(x_points, np.mean(data_dict[x_points[0]]), marker='o', color=color, label=label, zorder=2)
        return

    means = [np.mean(data_dict[x]) for x in x_points]

    percentile_levels = [(40, 60), (30, 70), (20, 80), (10, 90)]
    alphas = [0.5, 0.4, 0.3, 0.2]  # [0.3, 0.2, 0.1, 0.05]

    for (lower_p, upper_p), alpha in zip(percentile_levels, alphas):
        y_lower_points = [np.percentile(data_dict[x], lower_p) for x in x_points]
        y_upper_points = [np.percentile(data_dict[x], upper_p) for x in x_points]

        x_curve = np.linspace(min(x_points), max(x_points), 200)

        # Use a spline degree of 3 for a smooth curve if there are enough points.
        # Otherwise, fall back to linear interpolation.
        k = 3 if len(x_points) >= 4 else 1

        try:
            spline_lower = make_interp_spline(x_points, y_lower_points, k=k)
            y_lower_curve = spline_lower(x_curve)

            spline_upper = make_interp_spline(x_points, y_upper_points, k=k)
            y_upper_curve = spline_upper(x_curve)

            ax.fill_between(
                x_curve,
                y_lower_curve,
                y_upper_curve,
                color=color,
                alpha=alpha,
            )
        except ValueError as e:
            # Handle cases where spline cannot be created (e.g., duplicate x points)
            print(f"Error creating spline for data points: {x_points}. Falling back to linear fill. Error: {e}")
            ax.fill_between(
                x_points,
                y_lower_points,
                y_upper_points,
                color=color,
                alpha=alpha
            )

    # Plot a dashed line connecting the mean points
    ax.plot(
        x_points,
        means,
        color=color,
        linestyle='--',
        linewidth=1,
        marker='o',
        markersize=3,
        label=label,
        zorder=2
    )


def save_combined_df():
    # Define the pattern to find the CSV files
    base_dir = "../experiments"
    csv_pattern = os.path.join(base_dir, "*", "*", "*", "*_25_agents", "merged_record.csv")
    file_paths = glob.glob(csv_pattern)

    if not file_paths:
        print(f"No files found matching the pattern: {csv_pattern}")
        return

    # Load and combine all the dataframes
    k_values = [1, 5, 10, 15, 20, 25]
    total_agents = 25
    all_data_records = []

    for path in file_paths:
        try:
            df = pd.read_csv(path)
            parts = path.split(os.sep)
            noise = parts[-5]
            model_name = parts[-4]
            dataset = parts[-3]
            print(dataset, noise, model_name)

            for k in k_values:
                num_groups = total_agents - k + 1
                k_accuracies = []
                for i in range(num_groups):
                    group_cols = [f"answers_{d}" for d in range(i, i + k)]
                    group_df = df[group_cols].copy()

                    correct_predictions = 0
                    for _, row in group_df.iterrows():
                        agent_answers = row.tolist()
                        voted_answer = None
                        if dataset in ("gsm", "multiarith"):
                            voted_answer = get_majority_voting_answer_for_gsm(agent_answers)
                        elif dataset == "math":
                            voted_answer = get_majority_voting_answer_for_math(agent_answers)
                        elif dataset == "mmlu":
                            voted_answer = get_majority_voting_answer(agent_answers)

                        ground_truth = df.loc[_, 'ground_truth']
                        is_correct = 1 if voted_answer == ground_truth else 0
                        correct_predictions += is_correct

                    k_accuracies.append(correct_predictions / len(group_df))

                all_data_records.append({
                    'dataset': dataset,
                    'noise': noise,
                    'model': model_name,
                    'k': k,
                    'k_accuracies': np.array(k_accuracies)
                })
        except Exception as e:
            print(f"Error reading {path}: {e}")

    if not all_data_records:
        print("No valid data was loaded. Please check the directory structure and file paths.")
        return

    # Create a DataFrame from the records
    combined_df = pd.DataFrame(all_data_records)

    combined_df.to_csv("big_combination.csv", index=False)


def get_combined_df():
    df = pd.read_csv("big_combination.csv")
    df['k_accuracies'] = df['k_accuracies'].str.replace(r'\s+', ',', regex=True)
    df['k_accuracies'] = df['k_accuracies'].apply(ast.literal_eval)
    return df


def main():
    k_values = [1, 5, 10, 15, 20, 25]
    # save_combined_df()

    combined_df = get_combined_df()

    # --- Plotting Grid ---
    datasets = sorted(combined_df["dataset"].unique())
    noises = sorted(combined_df["noise"].unique())
    models = sorted(combined_df["model"].unique())

    fig, axes = plt.subplots(len(datasets), len(noises), figsize=(18, 12), sharey=True)

    # Use a color map for models
    colors = plt.cm.get_cmap('viridis', len(models))

    for i, dataset in enumerate(datasets):
        for j, noise in enumerate(noises):
            ax = axes[i, j] if len(datasets) > 1 else axes[j]
            ax.set_title(f"{noise.capitalize()}", fontsize=11)
            ax.set_xlabel("Agent Count")
            ax.set_ylabel("Accuracy")

            sub_df = combined_df[(combined_df["dataset"] == dataset) & (combined_df["noise"] == noise)]

            for k, model in enumerate(models):
                model_df = sub_df[sub_df["model"] == model]
                if model_df.empty:
                    continue

                data_for_plot = {
                    row['k']: row['k_accuracies']
                    for _, row in model_df.iterrows()
                }

                if data_for_plot:
                    plot_layered_volume(ax, data_for_plot, colors(k), model)

            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend(fontsize=8)
            ax.set_ylim(0, 1)  # Ensure accuracy is between 0 and 1
            ax.set_xticks(k_values)

            # Set row titles
            if j == 0:
                ax.set_ylabel(f"{dataset.upper()}\nAccuracy", fontsize=11)
            if i == 0:
                ax.set_title(f"{noise.capitalize()}", fontsize=11)

    fig.suptitle("Accuracy Distribution by Agent Count - Rows: Dataset, Cols: Noise", y=1.02, fontsize=14)
    plt.tight_layout()
    fig.savefig("viz_mean_std_graph.png", bbox_inches="tight", dpi=500)
    plt.show()


if __name__ == "__main__":
    main()
