import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger


load_dotenv()


PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
FEATURES_DIR = DATA_DIR / "features"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

DB_DIR = PROJ_ROOT / "database"
DB_PATH = DB_DIR / "fake_news.db"


APP_NAME = "Fake News Detector"
APP_VERSION = "1.0.0"
APP_ICON = "🔍"


DEFAULT_MODEL = "lightgbm"


AVAILABLE_MODELS = ["lightgbm", "randomforest", "bernoullinb", "multinomialnb"]


SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "te": "Telugu",
    "hinglish": "Hinglish",
}


RISK_THRESHOLDS = {
    "critical": 25,   
    "high": 50,       
    "medium": 75,     
    "low": 100,       
}


ROLES = ["reporter", "researcher", "admin"]


SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-random-string")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")




try:
    from tqdm import tqdm

    try:
        logger.remove()
    except Exception:
        pass
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
