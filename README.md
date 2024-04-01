# knittingtools

KnittingTools is a simple web app written in Python. It currently supports two main features:
* A knitting calculator
* A punchcard generator

## Dependencies:
* python 3.11
* [poetry](https://python-poetry.org/docs/#installation)

## Installation

Clone this repo to a local directory.

```bash
# create virtual environment
python3 -m venv ./.venv

# source the virtual environment
source .venv/bin/activate

# install dependencies (see pyproject.toml)
poetry install
```


## Running The Application

#### For development:
`uvicorn api:app --reload`
