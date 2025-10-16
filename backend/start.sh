#!/bin/bash

source .venv/bin/activate  # Windows esetén: .venv\Scripts\activate

pip install -r requirements.txt

python -m playwright install

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000