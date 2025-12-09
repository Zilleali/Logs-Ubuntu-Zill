#!/bin/bash
# Install all dependencies

echo "Installing Python dependencies..."

# Check if we're in venv, activate if not
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Activated virtual environment"
    else
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
    fi
fi

# Upgrade pip
pip install --upgrade pip

# Install from requirements
pip install -r requirements.txt

echo "✅ All dependencies installed!"
echo "Python: $(which python3)"
echo "Installed packages:"
pip list | grep -E "(flask|matplotlib|pandas|psutil)"