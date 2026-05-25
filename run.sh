#!/bin/bash
set -e
cd "$(dirname "$0")"

PYTHON=/opt/homebrew/bin/python3.12

if [ ! -d .venv ]; then
    echo "Setting up virtual environment..."
    "$PYTHON" -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
fi

exec .venv/bin/python app.py
