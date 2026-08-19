

import joblib
import yaml
from pathlib import Path

from loguru import logger
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier

from src.config import MODELS_DIR, FEATURES_DIR, PROJ_ROOT


def read_params(file_path: Path) -> dict:
    
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def save_model(model, save_dir: Path, model_name: str):
    
    save_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(value=model, filename=save_dir / model_name)


def train():
    
    params_path = PROJ_ROOT / "params.yaml"

    logger.info("Loading training features...")
    X_train = joblib.load(FEATURES_DIR / "X_train.pkl")
    y_train = joblib.load(FEATURES_DIR / "y_train.pkl")

    params = read_params(params_path)["Train"]

    models = {
        "MultinomialNB": MultinomialNB(**params.get("MultinomialNB", {})),
        "BernoulliNB": BernoulliNB(**params.get("BernoulliNB", {})),
        "RandomForest": RandomForestClassifier(**params.get("Random_Forest", {})),
        "LightGBM": LGBMClassifier(**params.get("LightGBM", {})),
    }

    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        save_model(model, MODELS_DIR, f"{name.lower()}.joblib")
        logger.info(f"Saved {name} to {MODELS_DIR}")

    logger.success("All models trained and saved! 🎉")


if __name__ == "__main__":
    train()