 # Fake News Detector

> **An end-to-end, production-oriented Fake News Detection platform built with modern ML and MLOps practices.**

This project goes beyond training a machine-learning model. It is a complete ML application covering the entire workflow — from **data versioning and preprocessing to model training, experiment tracking, model evaluation, API serving, frontend integration, CI/CD, and deployment**.

Built for **Devkriti** by **Utkarsh Gupta**,**Astitva Yadav** the system combines classical NLP with supervised machine learning to analyze news articles and provide a detailed assessment rather than simply returning a *Fake* or *Real* label.

The project follows an **MLOps-first architecture**, using **DVC** for data and pipeline versioning, **MLflow with DagsHub** for experiment tracking and model management, and **GitHub Actions** for automated CI/CD workflows.

On top of the ML pipeline, the application provides a **FastAPI backend** for model inference and a **React + Vite frontend** for interacting with the system.



## Features

| Feature | Description |
|---|---|
| 🔍 **Fake News Detection** | TF-IDF + LightGBM/RandomForest/NaiveBayes classifiers (98.5% F1) |
| 🏷️ **Multi-class Classification** | Detects propaganda, clickbait, hate speech, satire, AI-generated content |
| 💬 **Sentiment Analysis** | Polarity & subjectivity scoring to flag emotionally manipulative content |
| 🔑 **Entity & Keyword Extraction** | spaCy NER + frequency-based keyword extraction |
| 🎯 **Credibility Scoring** | Composite 0-100 score from 5 weighted signal sources |
| ✅ **Real-time Verification** | Cross-references articles against Reuters, AP, BBC, NYT, NDTV, etc. |
| 🌐 **Multi-language Support** | English, Hindi, Hinglish, Marathi, Telugu — auto-detection + translation |
| 📊 **Analytics Dashboard** | Interactive Plotly charts for trends, distributions, and insights |
| 🔐 **User Authentication** | Role-based access: Reporter, Researcher, Admin |
| 🔄 **CI/CD & Model Registry** | Automated DVC pipeline runs on GitHub Actions, logging to DagsHub MLflow |

## Model Performance

Trained on the [Kaggle Fake and Real News Dataset](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset) (~44K articles).

| Model | Accuracy | F1 (weighted) | ROC-AUC |
|---|---|---|---|
| **LightGBM** 🏆 | **98.54%** | **98.54%** | **99.90%** |
| Random Forest | 97.79% | 97.79% | 99.78% |
| Bernoulli NB | 94.27% | 94.26% | 98.08% |
| Multinomial NB | 92.70% | 92.70% | 97.70% |

---

## Quick Start

### Prerequisites
- Node.js (for frontend)
- Python 3.10+ (for backend)

### 1. Backend Setup (FastAPI)

```bash
# Clone and install
git clone https://github.com/utkarshhg/Fake-news-detection.git
cd Fake-news-detection

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords punkt

# Copy and configure environment
cp .env.example .env

# Run FastAPI backend
uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup (React)

Open a new terminal window:
```bash
cd Fake-news-detection/frontend
npm install
npm run dev
```

Open `http://localhost:5173` — default login: `admin` / `admin123`

---

## Project Structure

```text
├── api.py                        ← FastAPI backend entry point
├── requirements.txt              ← Python dependencies
├── dvc.yaml / params.yaml        ← ML pipeline config
├── .github/workflows/ci.yml      ← Automated CI/CD action
│
├── frontend/                     ← React Web App (Vite)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/                      
│       ├── api/client.js         ← Backend integration
│       ├── components/           ← Reusable UI blocks
│       ├── context/AuthContext   ← JWT State management
│       └── pages/                ← Dashboard, Analyzer, etc.
│
├── src/                          ← Python Backend Core
│   ├── auth/                     ← JWT Authentication
│   ├── database/                 ← SQLite + SQLAlchemy ORM
│   ├── modeling/                 ← ML Training & Eval scripts
│   └── nlp/                      ← Text cleaning, Entity, Sentiment
│
├── data/                         ← DVC-managed raw/processed datasets
├── models/                       ← DVC-managed trained classifiers
└── deploy/                       ← AWS EC2 and Nginx config files
```

---

## ML Pipeline (DVC & DagsHub)

This project uses **DVC** for data versioning and **DagsHub** for remote storage and MLflow tracking. A GitHub Actions pipeline automatically retrains models when new data/code is pushed.

```bash
# Authenticate with DagsHub (if running locally)
# Make sure DAGSHUB_USER_TOKEN is in your .env
dvc pull -r origin

# Run the full ML pipeline locally
dvc repro
```

Pipeline stages (`data_cleaning`, `featurize`, `train_models`, `evaluate`) are defined in `dvc.yaml` and tracked with DVC. Metrics are pushed live to your remote DagsHub MLflow dashboard.

---

## How It Works

**1. Input** → Paste article text or enter a URL (auto-fetched via newspaper3k).

**2. Language Detection** → Auto-detects English, Hindi, Hinglish, Marathi, Telugu. Non-English text is translated to English for analysis.

**3. ML Prediction** → Cleaned text → TF-IDF → LightGBM (or selected model) → FAKE/REAL with confidence.

**4. Sentiment Analysis** → TextBlob polarity/subjectivity with suspicious pattern flagging.

**5. Entity Extraction** → spaCy NER (persons, orgs, locations) + keyword frequency analysis.

**6. Content Classification** → Pattern-based detection of propaganda, clickbait, hate speech, satire, AI-generated content.

**7. Source Verification** → Keywords queried against NewsAPI.org / Google News to find matching reports from trusted outlets.

**8. Credibility Score** → Weighted composite (ML 50% + Verification 10% + Sentiment 15% + Content 15% + Entities 10%) → 0-100 score + risk level.

## 🌐 Supported Languages

* English
* Hindi
* Hinglish
* Marathi
* Telugu


## User Roles

| Role | Permissions |
|---|---|
| **Reporter** | Analyze articles, view own history |
| **Researcher** | Analyze, view all history, export data, access dashboard |
| **Admin** | All above + user management, system stats, flagged article review |


