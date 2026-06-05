@echo off
cd /d "%~dp0"

if not exist .venv (
    echo Setting up virtual environment...
    python -m venv .venv
    .venv\Scripts\pip install -q -U -r requirements.txt
)

.venv\Scripts\python app.py
