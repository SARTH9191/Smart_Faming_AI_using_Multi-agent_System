#!/usr/bin/env python
"""
Startup script for AgroBrain OS
"""

import uvicorn
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 50)
    print("AgroBrain OS v3.0.0 - Starting...")
    print("=" * 50)

    from main import app

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
