#!/usr/bin/env python3
"""
Check if all required imports are available
"""

import sys
import os

print("=== Checking Imports ===")
print(f"Python path: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")
print()

# Check each import
imports_to_check = [
    "flask",
    "matplotlib",
    "matplotlib.pyplot",
    "pandas",
    "psutil",
    "json",
    "datetime",
    "subprocess",
    "socket",
    "platform",
    "uuid",
    "getpass",
    "statistics",
    "collections",
    "glob"
]

print("Import Status:")
print("-" * 40)

all_ok = True
for module in imports_to_check:
    try:
        if "." in module:
            # Handle submodules like matplotlib.pyplot
            parts = module.split(".")
            exec(f"import {parts[0]}")
            for part in parts[1:]:
                exec(f"{parts[0]} = {parts[0]}.{part}")
        else:
            __import__(module)
        print(f"✅ {module:20s} - OK")
    except ImportError as e:
        print(f"❌ {module:20s} - MISSING: {e}")
        all_ok = False
    except Exception as e:
        print(f"⚠️  {module:20s} - ERROR: {e}")

print("-" * 40)

if all_ok:
    print("✅ All imports are available!")
else:
    print("❌ Some imports are missing.")
    print("\nTo fix, run:")
    print("  cd ~/simple-logs && ./install-deps.sh")
    print("\nOr install manually:")
    print("  pip install flask matplotlib pandas psutil")

# Check specific psutil functions
print("\n=== Checking psutil functions ===")
try:
    import psutil
    print(f"✅ psutil version: {psutil.__version__}")
    print(f"✅ CPU percent: {psutil.cpu_percent(interval=0.1)}%")
    print(f"✅ Memory: {psutil.virtual_memory().percent}%")
    print(f"✅ Disk: {psutil.disk_usage('/').percent}%")
except Exception as e:
    print(f"❌ psutil test failed: {e}")