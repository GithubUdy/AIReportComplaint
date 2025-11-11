
#!/usr/bin/env bash
set -e
pip install -r requirements.txt
python ml/train.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
