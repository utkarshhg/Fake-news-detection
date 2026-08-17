

import joblib
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
import typer
import mlflow
import mlflow.sklearn
import dagshub
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    RocCurveDisplay,
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
)

from src.config import MODELS_DIR, FEATURES_DIR, FIGURES_DIR, PROJ_ROOT

app = typer.Typer()


@app.command()
def main(
    features_path: Path = FEATURES_DIR,
    model_dir: Path = MODELS_DIR,
    figures_dir: Path = FIGURES_DIR,
):
    
    
    figures_dir.mkdir(parents=True, exist_ok=True)

    
    if os.getenv("DAGSHUB_USER_TOKEN") or os.getenv("MLFLOW_TRACKING_URI"):
        logger.info("Initializing DagsHub for MLflow tracking...")
        dagshub.init(repo_owner='utkarshhg', repo_name='Fake-news-detection', mlflow=True)
    else:
        logger.info("Using local SQLite MLflow tracking...")
        mlflow.set_tracking_uri(f"sqlite:///{PROJ_ROOT / 'mlflow.db'}")
    mlflow.set_experiment("Fake_News_Evaluation")

    
    logger.info("Loading test features...")
    X_test = joblib.load(features_path / "X_test.pkl")
    y_test = joblib.load(features_path / "y_test.pkl")

    
    model_files = [f for f in model_dir.glob("*.joblib") if "tfidf" not in f.name]

    if not model_files:
        logger.error(f"No model files found in {model_dir}")
        raise typer.Exit(1)

    
    all_metrics = {}

    for model_path in model_files:
        model_name = model_path.stem
        logger.info(f"Evaluating {model_name}...")
        model = joblib.load(model_path)

        with mlflow.start_run(run_name=f"Eval_{model_name}"):
            y_pred = model.predict(X_test)
            y_probs = model.predict_proba(X_test)[:, 1]

            
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average="weighted"),
                "recall": recall_score(y_test, y_pred, average="weighted"),
                "f1": f1_score(y_test, y_pred, average="weighted"),
                "roc_auc": roc_auc_score(y_test, y_probs),
            }

            all_metrics[model_name] = metrics
            mlflow.log_metrics(metrics)

            
            fig, ax = plt.subplots(figsize=(8, 6))
            RocCurveDisplay.from_predictions(y_test, y_probs, ax=ax)
            ax.set_title(f"ROC Curve: {model_name}", fontsize=14, fontweight="bold")
            ax.grid(alpha=0.3)
            roc_path = figures_dir / f"{model_name}_roc.png"
            fig.savefig(roc_path, dpi=150, bbox_inches="tight")
            mlflow.log_artifact(str(roc_path))
            plt.close(fig)

            
            fig, ax = plt.subplots(figsize=(7, 6))
            cm = confusion_matrix(y_test, y_pred)
            disp = ConfusionMatrixDisplay(cm, display_labels=["Fake", "Real"])
            disp.plot(ax=ax, cmap="Blues", values_format="d")
            ax.set_title(f"Confusion Matrix: {model_name}", fontsize=14, fontweight="bold")
            cm_path = figures_dir / f"{model_name}_confusion_matrix.png"
            fig.savefig(cm_path, dpi=150, bbox_inches="tight")
            mlflow.log_artifact(str(cm_path))
            plt.close(fig)

            
            report = classification_report(y_test, y_pred, target_names=["Fake", "Real"])
            report_path = figures_dir / f"{model_name}_classification_report.txt"
            report_path.write_text(report)
            mlflow.log_artifact(str(report_path))

            logger.info(
                f"{model_name} | Acc: {metrics['accuracy']:.4f} | "
                f"F1: {metrics['f1']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f}"
            )

    
    metrics_path = PROJ_ROOT / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=4)

    logger.success(f"Evaluation complete! Metrics saved to {metrics_path}. 🎉")
    logger.success(f"Figures saved to {figures_dir}")


if __name__ == "__main__":
    app()