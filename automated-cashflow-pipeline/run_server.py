import uvicorn
import os
import sys

# Ensure we're importing from the current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the api module explicitly
import api

print(f"Starting server with app: {api.app}")
print(f"App title: {api.app.title}")
print(f"App version: {api.app.version}")
print(f"Routes: {[r.path for r in api.app.routes]}")

if __name__ == "__main__":
    uvicorn.run(api.app, host="0.0.0.0", port=8002, reload=False)