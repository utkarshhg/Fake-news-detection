import joblib
from pathlib import Path
import pandas as pd
from loguru import logger
import typer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer


from src.config import MODELS_DIR, PROCESSED_DATA_DIR

app = typer.Typer()

@app.command()
def main(
    input_path: Path = PROCESSED_DATA_DIR / "processed_dataset.csv",
):
    
    logger.info(f"Loading processed data from {input_path}...")
    df = pd.read_csv(input_path)
    
  
    df.dropna(subset=['review', 'sentiment'], inplace=True)
    
   
    logger.info("Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['review'], 
        df['sentiment'], 
        test_size=0.2, 
        random_state=42, 
        stratify=df['sentiment'] 
    )

   
    logger.info("Vectorizing text using TF-IDF...")
    tfidf_vectorizer = TfidfVectorizer(max_features=5000)
    
 
    tfidf_vectorizer.fit(X_train)
    
    
    X_train_transformed = tfidf_vectorizer.transform(X_train)
    X_test_transformed = tfidf_vectorizer.transform(X_test)
    
    
    logger.info("Saving processed features...")
    
    
    feat_dir = Path("data/features")
    feat_dir.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    
    joblib.dump(X_train_transformed, feat_dir / "X_train.pkl")
    joblib.dump(X_test_transformed, feat_dir / "X_test.pkl")
    
    
    joblib.dump(y_train, feat_dir / "y_train.pkl")
    joblib.dump(y_test, feat_dir / "y_test.pkl")
    
    
    joblib.dump(tfidf_vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")

    logger.success("Data Splitting and Vectorization complete! 🎉")

if __name__ == "__main__":
    app()