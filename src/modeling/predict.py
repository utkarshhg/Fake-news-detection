

import joblib
from pathlib import Path
from typing import Optional

from loguru import logger
import typer

from src.config import MODELS_DIR, DEFAULT_MODEL, AVAILABLE_MODELS
from src.dataset import clean_text

app = typer.Typer()


def load_model_and_vectorizer(
    model_name: str = DEFAULT_MODEL,
    models_dir: Path = MODELS_DIR,
) -> tuple:
    
    model_path = models_dir / f"{model_name}.joblib"
    vectorizer_path = models_dir / "tfidf_vectorizer.joblib"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}. "
            f"Available models: {AVAILABLE_MODELS}"
        )
    if not vectorizer_path.exists():
        raise FileNotFoundError(
            f"TF-IDF vectorizer not found: {vectorizer_path}. "
            "Run the featurize pipeline first."
        )

    logger.info(f"Loading model '{model_name}' from {model_path}")
    model = joblib.load(model_path)

    logger.info(f"Loading TF-IDF vectorizer from {vectorizer_path}")
    vectorizer = joblib.load(vectorizer_path)

    return model, vectorizer


def predict_text(
    text: str,
    model=None,
    vectorizer=None,
    model_name: str = DEFAULT_MODEL,
) -> dict:
    
    if model is None or vectorizer is None:
        model, vectorizer = load_model_and_vectorizer(model_name)

    
    cleaned = clean_text(text)

    if not cleaned.strip():
        logger.warning("Text is empty after cleaning.")
        return {
            "label": "UNKNOWN",
            "confidence": 0.0,
            "fake_probability": 0.5,
            "real_probability": 0.5,
            "model_used": model_name,
        }

    
    features = vectorizer.transform([cleaned])

    
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    
    fake_prob = float(probabilities[0])
    real_prob = float(probabilities[1])

    label = "REAL" if prediction == 1 else "FAKE"
    confidence = real_prob if prediction == 1 else fake_prob

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "fake_probability": round(fake_prob, 4),
        "real_probability": round(real_prob, 4),
        "model_used": model_name,
    }


def predict_batch(
    texts: list[str],
    model=None,
    vectorizer=None,
    model_name: str = DEFAULT_MODEL,
) -> list[dict]:
    
    if model is None or vectorizer is None:
        model, vectorizer = load_model_and_vectorizer(model_name)

    return [
        predict_text(text, model=model, vectorizer=vectorizer, model_name=model_name)
        for text in texts
    ]


@app.command()
def main(
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Article text to classify"),
    model_name: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Model to use"),
):
    
    if text is None:
        logger.info("No --text provided. Enter article text (Ctrl+D / Ctrl+Z to finish):")
        import sys
        text = sys.stdin.read()

    result = predict_text(text, model_name=model_name)

    logger.info(f"Model: {result['model_used']}")
    logger.info(f"Prediction: {result['label']}")
    logger.info(f"Confidence: {result['confidence']:.2%}")
    logger.info(f"Fake probability: {result['fake_probability']:.2%}")
    logger.info(f"Real probability: {result['real_probability']:.2%}")

    return result


if __name__ == "__main__":
    app()
