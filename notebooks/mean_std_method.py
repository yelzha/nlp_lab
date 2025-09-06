from collections import Counter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import math

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


def calculate_accuracy(df: pd.DataFrame, num_agents: int, num_simulations: int = 100) -> pd.DataFrame:
    """
    Calculates mean and standard deviation of accuracy for a given number of agents.
    Simulates the process multiple times for robustness.
    """
    results = []

    for simulation in range(num_simulations):
        accuracies = []
        for index, row in df.iterrows():
            ground_truth = str(row['ground_truth'])
            agent_answers = [str(row[f'answers_{i}']) for i in range(25)]

            # Randomly select `num_agents` from the list of 25 available answers
            sampled_answers = np.random.choice(agent_answers, num_agents, replace=False)

            # Get the majority voted answer
            if row['dataset'] == "gsm" or row['dataset'] == "multiarith":
                voted_answer = get_majority_voting_answer_for_gsm(sampled_answers)
            elif row['dataset'] == "math":
                voted_answer = get_majority_voting_answer_for_math(sampled_answers)
            elif row['dataset'] == "mmlu":
                voted_answer = get_majority_voting_answer(sampled_answers)

            # Compare the voted answer with the ground truth
            # Use .strip() and .lower() for robust comparison
            is_correct = 1 if str(voted_answer).strip().lower() == ground_truth.strip().lower() else 0
            accuracies.append(is_correct)

        # Calculate the accuracy for this simulation run
        model = df['model'].iloc[0] if 'model' in df.columns else 'Unknown'
        dataset = df['dataset'].iloc[0] if 'dataset' in df.columns else 'Unknown'
        noise = df['noise'].iloc[0] if 'noise' in df.columns else 'Unknown'

        results.append({
            'model': model,
            'dataset': dataset,
            'noise': noise,
            'num_agents': num_agents,
            'accuracy': np.mean(accuracies)
        })

    return pd.DataFrame(results)


def main():
    # Define the pattern to find the CSV files
    csv_pattern = 'experiments/*/log_gsm_r2ata_25_agents/merged.csv'
    base_path = Path('.')
    file_paths = list(base_path.glob(csv_pattern))

    if not file_paths:
        print(f"No files found matching the pattern: {csv_pattern}")
        return

    # Load and combine all the dataframes
    all_data_frames = []
    for path in file_paths:
        try:
            df = pd.read_csv(path)
            # Add columns from the file path to help with grouping
            parts = path.parts
            model_name = parts[1]
            dataset = parts[2]
            noise = parts[3]
            df['model'] = model_name
            df['dataset'] = dataset
            df['noise'] = noise
            all_data_frames.append(df)
        except Exception as e:
            print(f"Error reading {path}: {e}")

    if not all_data_frames:
        print("No valid data frames were loaded.")
        return

    combined_df = pd.concat(all_data_frames, ignore_index=True)

    # Define the number of agents to plot
    agent_group_sizes = [1, 5, 10, 15, 20, 25]
    num_simulations = 100

    # Calculate accuracies for each group size and combine results
    final_df_list = []
    for num_agents in agent_group_sizes:
        print(f"Calculating accuracies for {num_agents} agents...")
        for name, group in combined_df.groupby(['model', 'noise', 'dataset']):
            acc_df = calculate_accuracy(group, num_agents, num_simulations=num_simulations)
            final_df_list.append(acc_df)

    if not final_df_list:
        print("No results to plot.")
        return

    final_df = pd.concat(final_df_list, ignore_index=True)

    # Get unique values for plotting
    datasets = sorted(final_df['dataset'].unique())
    noises = sorted(final_df['noise'].unique())
    models = sorted(final_df['model'].unique())

    # Create the 4x6 grid plot
    fig, axes = plt.subplots(len(datasets), len(noises), figsize=(18, 16), sharey=True)
    fig.suptitle("Accuracy vs. Number of Agents (4x6 Grid)", fontsize=16, y=1.02)

    # If there's only one row or column, axes is not a 2D array
    if len(datasets) == 1 and len(noises) == 1:
        axes = np.array([[axes]])
    elif len(datasets) == 1:
        axes = np.expand_dims(axes, axis=0)
    elif len(noises) == 1:
        axes = np.expand_dims(axes, axis=1)

    for i, dataset in enumerate(datasets):
        for j, noise in enumerate(noises):
            ax = axes[i, j]

            # Filter data for the current subplot
            plot_df = final_df[(final_df['dataset'] == dataset) & (final_df['noise'] == noise)]

            if plot_df.empty:
                continue

            # Plot using seaborn's lineplot for mean and standard deviation
            sns.lineplot(
                data=plot_df,
                x='num_agents',
                y='accuracy',
                hue='model',
                ax=ax,
                marker='o',
                errorbar=('sd'),  # Show standard deviation
            )

            # Set titles and labels
            if i == 0:
                ax.set_title(f'Noise: {noise}', fontsize=12)
            if j == 0:
                ax.set_ylabel(f'Accuracy ({dataset.upper()})', fontsize=12)
            else:
                ax.set_ylabel('')

            ax.set_xlabel('Number of Agents', fontsize=12)
            ax.set_xticks(agent_group_sizes)
            ax.set_ylim(0, 1)
            ax.grid(True, linestyle='--', alpha=0.6)

            # Adjust legend
            handles, labels = ax.get_legend_handles_labels()
            # Remove the 'model' title from the legend
            if ax.legend_:
                ax.legend_.set_title('')

    # Adjust layout and save the plot
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig('accuracy_vs_agents_plot.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    main()