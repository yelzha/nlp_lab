import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def load_data(csv_path: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path.resolve()}")
    df = pd.read_csv(path)
    required_cols = {"model", "dataset", "noise", "agent_num", "accuracy"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    # Ensure expected dtypes
    df["agent_num"] = pd.to_numeric(df["agent_num"], errors="coerce")
    df["accuracy"] = pd.to_numeric(df["accuracy"], errors="coerce")
    df = df.dropna(subset=["agent_num", "accuracy"])
    return df

def plot_grid_models_by_noise(df: pd.DataFrame, save_path: Path = None):
    """
    4x4 grid:
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

            if i == 0 and j == 0:
                ax.legend(fontsize=8)

    fig.suptitle("Accuracy by Agent Num — Rows: Dataset, Cols: Noise, Labels: Models", y=1.02, fontsize=14)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=200)
    plt.show()

def plot_means_by_noise(df: pd.DataFrame, save_path: = None):
    """
    2x2 grid of dataset-level mean accuracy per noise (across models).
    """
    datasets = sorted(df["dataset"].unique())
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=True)

    for ax, dataset in zip(axes.flatten(), datasets):
        sub = df[df["dataset"] == dataset]
        mean_df = (
            sub.groupby(["noise", "agent_num"], as_index=False)["accuracy"]
            .mean()
            .sort_values(["noise", "agent_num"])
        )
        for noise, g in mean_df.groupby("noise"):
            ax.plot(g["agent_num"], g["accuracy"], marker="o", label=noise)

        ax.set_title(dataset.upper())
        ax.set_xlabel("Agent Num")
        ax.set_ylabel("Accuracy")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(title="Noise", fontsize=8)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=200)
    plt.show()

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "./merged_results.csv"
    df = load_data(csv_path)

    # 4x4 grid (rows = datasets, cols = noise, labels = models)
    plot_grid_models_by_noise(df, save_path="grid_models_by_noise.png")

if __name__ == "__main__":
    main()