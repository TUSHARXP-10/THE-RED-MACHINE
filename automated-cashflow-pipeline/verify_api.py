import os
import sys

# Print current working directory
print("Current working directory:", os.getcwd())

# Print Python path
print("Python path:")
for path in sys.path:
    print(f"  {path}")

# Try to find all api.py files
print("\nSearching for api.py files:")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'api.py':
            full_path = os.path.abspath(os.path.join(root, file))
            print(f"  Found: {full_path}")

# Import the api module
print("\nImporting api module...")
import api
print(f"api.py location: {api.__file__}")
print(f"App title: {api.app.title}")
print(f"App version: {api.app.version}")

# Check FastAPI app details
print(f"App object: {api.app}")
print(f"App routes:")
for route in api.app.routes:
    print(f"  {route.path} -> {route.name}")

# Test the app directly using FastAPI test client
from fastapi.testclient import TestClient
client = TestClient(api.app)

print("\nTesting root endpoint:")
response = client.get("/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\nTesting health endpoint:")
response = client.get("/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")