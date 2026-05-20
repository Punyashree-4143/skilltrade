#!/usr/bin/env python3
"""
SkillTrade FastAPI Backend - Entry Point
"""

import uvicorn
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
os.chdir(current_dir)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "true").lower() == "true",
        log_level="info",
        access_log=True
    )
