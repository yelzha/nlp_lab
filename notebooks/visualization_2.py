import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

NOISES_TO_COMPARE = ["punctuation_10", "punctuation_30", "punctuation_50", "r2ata", "wikitypo"]

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

def compute_abs_diff_vs_clean(df: pd.DataFrame, noises: list[str]) -> pd.DataFrame:
    """Return rows for the given noises with abs_diff = |accuracy(noise) - accuracy(clean)|,
    matched on (model, dataset, agent_num)."""
    if "clean" not in df["noise"].unique():
        raise ValueError("No 'clean' rows found in the CSV. Cannot compute differences.")

    # Clean baseline per (model, dataset, agent_num)
    clean = (
        df[df["noise"] == "clean"]
        .loc[:, ["model", "dataset", "agent_num", "accuracy"]]
        .rename(columns={"accuracy": "clean_acc"})
    )

    # Only the noises we care about
    noisy = df[df["noise"].isin(noises)].copy()

    merged = noisy.merge(
        clean,
        on=["model", "dataset", "agent_num"],
        how="inner",
        validate="many_to_one",  # many noisy rows to one clean baseline
    )

    merged["abs_diff"] = (merged["accuracy"] - merged["clean_acc"]).abs()
    return merged.loc[:, ["model", "dataset", "noise", "agent_num", "abs_diff"]]

def plot_absdiff_grid(diff_df: pd.DataFrame, noises: list[str], save_path: Path | None = None):
    """
    Grid of subplots:
      - Rows  : dataset (expected 4)
      - Cols  : noise types (absolute difference vs clean)
      - Lines : models (abs_diff vs agent_num)
    """
    datasets = sorted(diff_df["dataset"].unique())
    model_order = sorted(diff_df["model"].unique())
    col_order = [n for n in noises if n in diff_df["noise"].unique()]

    n_rows = len(datasets)
    n_cols = len(col_order)
    if n_cols == 0:
        raise ValueError("None of the requested noise types are present in the data.")

    # Scale figure to keep it readable
    fig_w = max(3.2 * n_cols, 10)
    fig_h = max(2.8 * n_rows, 8)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h), sharey=True)

    # If there's only one row/col, axes may not be 2D
    if n_rows == 1 and n_cols == 1:
        axes = [[axes]]
    elif n_rows == 1:
        axes = [axes]
    elif n_cols == 1:
        axes = [[ax] for ax in axes]

    # Get a common y-limit for consistency (optional but helps comparison)
    y_max = diff_df["abs_diff"].max()
    y_pad = 0.02 if pd.notna(y_max) else 0.0

    for i, dataset in enumerate(datasets):
        for j, noise in enumerate(col_order):
            ax = axes[i][j]
            sub = diff_df[(diff_df["dataset"] == dataset) & (diff_df["noise"] == noise)]

            for model in model_order:
                g = sub[sub["model"] == model].sort_values("agent_num")
                if g.empty:
                    continue
                ax.plot(g["agent_num"], g["abs_diff"], marker="o", label=model)

            if i == 0:
                ax.set_title(noise, fontsize=11)
            if j == 0:
                ax.set_ylabel(f"{dataset.upper()}\n|Δ accuracy| vs clean", fontsize=10)
            ax.set_xlabel("Agent Num", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(title="Model", fontsize=8, title_fontsize=9)

            if pd.notna(y_max):
                ax.set_ylim(0, y_max + y_pad)

            if sub.empty:
                ax.text(
                    0.5, 0.5, "No data",
                    ha="center", va="center", transform=ax.transAxes, fontsize=9, alpha=0.7
                )

    fig.suptitle("Absolute Accuracy Difference vs Clean — Rows: Dataset, Cols: Noise, Lines: Models", y=0.995, fontsize=14)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=200)
    plt.show()


def main():
    csv_path = "./merged_results.csv"
    df = load_data(csv_path)
    diff_df = compute_abs_diff_vs_clean(df, NOISES_TO_COMPARE)
    plot_absdiff_grid(diff_df, NOISES_TO_COMPARE, save_path=Path("absdiff_grid_vs_clean.png"))


if __name__ == "__main__":
    main()
