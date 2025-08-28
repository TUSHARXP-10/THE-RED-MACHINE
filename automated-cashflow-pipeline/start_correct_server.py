#!/usr/bin/env python3
import os
import sys
import uvicorn
from pathlib import Path

# Force the correct working directory
project_dir = Path(__file__).parent
os.chdir(project_dir)

# Ensure the current directory is first in Python path
sys.path.insert(0, str(project_dir))

# Import the correct api module
import api

print(f"Starting server from: {project_dir}")
print(f"API title: {api.app.title}")
print(f"API version: {api.app.version}")
print(f"Available routes: {[route.path for route in api.app.routes]}")

# Start the server with explicit module reference
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8002, reload=False, log_level="info")