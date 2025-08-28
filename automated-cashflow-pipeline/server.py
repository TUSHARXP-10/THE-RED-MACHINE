import uvicorn
import os
import sys

# Force Python to use the local api.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Clear any cached modules
modules_to_clear = [m for m in sys.modules.keys() if m.startswith('api')]
for module in modules_to_clear:
    del sys.modules[module]

# Import the api module fresh
import api

print("=== Server Configuration ===")
print(f"App object: {api.app}")
print(f"App title: {api.app.title}")
print(f"App version: {api.app.version}")
print("Routes:")
for route in api.app.routes:
    print(f"  - {route.path} ({route.methods})")
print("============================")

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )