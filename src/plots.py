

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
import typer

from src.config import FIGURES_DIR, PROCESSED_DATA_DIR

app = typer.Typer()


def plot_model_comparison(metrics: dict, output_path: Path = None):
    
    if output_path is None:
        output_path = FIGURES_DIR / "model_comparison.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    models = list(metrics.keys())
    metric_names = list(next(iter(metrics.values())).keys())
    n_models = len(models)
    n_metrics = len(metric_names)

    x = np.arange(n_models)
    width = 0.8 / n_metrics

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, metric in enumerate(metric_names):
        values = [metrics[m][metric] for m in models]
        bars = ax.bar(x + i * width, values, width, label=metric.capitalize())
        ax.bar_label(bars, fmt="%.3f", fontsize=7, padding=2)

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Model Performance Comparison", fontsize=14, fontweight="bold")
    ax.set_xticks(x + width * (n_metrics - 1) / 2)
    ax.set_xticklabels(models, rotation=15)
    ax.legend(loc="lower right")
    ax.set_ylim(0.85, 1.02)
    ax.grid(axis="y", alpha=0.3)

    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Model comparison plot saved to {output_path}")


def plot_label_distribution(labels, output_path: Path = None):
    
    if output_path is None:
        output_path = FIGURES_DIR / "label_distribution.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    unique, counts = np.unique(labels, return_counts=True)
    names = ["Fake" if v == 0 else "Real" for v in unique]
    colors = ["#FF6B6B", "#4ECDC4"]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(names, counts, color=colors, edgecolor="white", linewidth=1.5)
    ax.bar_label(bars, fmt="%d", fontsize=12, fontweight="bold")
    ax.set_title("Dataset Label Distribution", fontsize=14, fontweight="bold")
    ax.set_ylabel("Number of Articles", fontsize=12)
    ax.grid(axis="y", alpha=0.3)

    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Label distribution plot saved to {output_path}")


@app.command()
def main(
    output_dir: Path = FIGURES_DIR,
):
    
    import json

    output_dir.mkdir(parents=True, exist_ok=True)

    
    metrics_path = PROCESSED_DATA_DIR.parent.parent / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            metrics = json.load(f)
        plot_model_comparison(metrics, output_dir / "model_comparison.png")
        logger.success("Report plots generated. 🎉")
    else:
        logger.warning(f"metrics.json not found at {metrics_path}. Run evaluate first.")


if __name__ == "__main__":
    app()
