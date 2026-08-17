import re
from pathlib import Path

import pandas as pd
import typer
from loguru import logger
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tqdm import tqdm

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
app = typer.Typer()


STOP_WORDS = set(stopwords.words("english"))
STEMMER = PorterStemmer()

def clean_text(text: str) -> str:
    
    if not isinstance(text, str):
        return ""
        
    
    text = re.sub(r'<.*?>', '', text)
    
    
    text = text.lower()
    
    
    text = re.sub(r'^.*?\(reuters\)\s*-\s*', '', text, flags=re.IGNORECASE)
    
    
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    
    return " ".join([STEMMER.stem(word) for word in text.split() if word not in STOP_WORDS])


@app.command()
def main(
    true_path: Path = RAW_DATA_DIR / "True.csv",
    fake_path: Path = RAW_DATA_DIR / "Fake.csv",
    output_path: Path = PROCESSED_DATA_DIR / "processed_dataset.csv",
):
    
    logger.info("Loading raw True and Fake datasets...")
    df_true = pd.read_csv(true_path)
    df_false = pd.read_csv(fake_path)
    
    logger.info("Assigning sentiments and merging...")
    df_true['sentiment'] = 1
    df_false['sentiment'] = 0
    df = pd.concat([df_false, df_true], axis=0)
    
    logger.info("Dropping unnecessary columns and duplicates...")
    columns_to_drop = ['date', 'title', 'subject']
    df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True, errors='ignore')
    
    df.drop_duplicates(inplace=True)
    df.rename(columns={'text': 'review'}, inplace=True)
    
    
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info("Applying text cleaning pipeline (this may take a few minutes)...")
    tqdm.pandas() 
    df['review'] = df['review'].progress_apply(clean_text) 
    
    logger.info(f"Saving fully processed dataset to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    logger.success("Data processing complete! 🎉")


if __name__ == "__main__":
    app()