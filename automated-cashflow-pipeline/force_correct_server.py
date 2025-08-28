#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Get the absolute path to the current directory
project_dir = Path(__file__).parent.absolute()
print(f"Project directory: {project_dir}")

# Ensure we're using the correct directory
os.chdir(project_dir)

# Force the correct module import by clearing and rebuilding sys.path
sys.path.insert(0, str(project_dir))

# Import the specific api.py file
import importlib.util
spec = importlib.util.spec_from_file_location("api", project_dir / "api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

# Verify we're loading the correct app
print(f"App title: {api.app.title}")
print(f"App version: {api.app.version}")
print(f"Routes: {[route.path for route in api.app.routes]}")

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api.app, host="0.0.0.0", port=8002, log_level="info")