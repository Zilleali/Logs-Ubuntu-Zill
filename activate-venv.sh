#!/bin/bash
# Activate virtual environment for logs system

cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "Python: $(which python3)"