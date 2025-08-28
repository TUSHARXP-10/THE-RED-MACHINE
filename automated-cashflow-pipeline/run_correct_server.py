#!/usr/bin/env python3
import os
import sys
import uvicorn

# Ensure we're in the correct directory
os.chdir('C:\\Users\\tushar\\Desktop\\THE-RED MACHINE\\automated-cashflow-pipeline')

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

# Import the api module explicitly
import importlib.util
spec = importlib.util.spec_from_file_location('api', 'api.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

print("=== Server Configuration ===")
print(f"API file: {os.path.abspath('api.py')}")
print(f"App: {api.app}")
print(f"Title: {api.app.title}")
print(f"Version: {api.app.version}")
print("Routes:")
for route in api.app.routes:
    print(f"  - {route.path} ({route.methods})")
print("============================")

if __name__ == "__main__":
    uvicorn.run(
        api.app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )