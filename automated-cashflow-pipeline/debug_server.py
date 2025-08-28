import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our api module
import api

# Print debug information
print("Loading app from:", api.__file__)
print("App title:", api.app.title)
print("App version:", api.app.version)
print("Available routes:")
for route in api.app.routes:
    print(f"  {route.path} -> {route.name}")

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api.app, host="0.0.0.0", port=8002)