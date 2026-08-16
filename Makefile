#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = fake-news-detection
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	$(PYTHON_INTERPRETER) -m spacy download en_core_web_sm
	$(PYTHON_INTERPRETER) -m nltk.downloader stopwords punkt

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using ruff
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format

## Make dataset (clean raw data)
.PHONY: data
data:
	$(PYTHON_INTERPRETER) src/dataset.py

## Run featurization
.PHONY: featurize
featurize:
	$(PYTHON_INTERPRETER) src/features.py

## Train all models
.PHONY: train
train:
	$(PYTHON_INTERPRETER) src/modeling/train.py

## Evaluate models
.PHONY: evaluate
evaluate:
	$(PYTHON_INTERPRETER) src/modeling/evaluate.py

## Run full ML pipeline
.PHONY: pipeline
pipeline: data featurize train evaluate

## Run Streamlit app locally
.PHONY: streamlit
streamlit:
	streamlit run streamlit_app.py --server.port 8501

## Build Docker image
.PHONY: docker-build
docker-build:
	docker build -t fake-news-detector:latest .

## Run Docker container
.PHONY: docker-run
docker-run:
	docker run -p 8501:8501 --env-file .env -v fake_news_data:/app/database fake-news-detector:latest

## Run tests
.PHONY: test
test:
	pytest tests/ -v

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "$${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
