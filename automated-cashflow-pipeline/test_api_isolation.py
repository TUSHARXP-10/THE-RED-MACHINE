import os
import sys

# Ensure we're in the right directory
os.chdir('C:\\Users\\tushar\\Desktop\\THE-RED MACHINE\\automated-cashflow-pipeline')

# Clear any existing modules
modules_to_clear = [m for m in list(sys.modules.keys()) if m.startswith('api')]
for module in modules_to_clear:
    del sys.modules[module]

# Import the api module using absolute path
import importlib.util
spec = importlib.util.spec_from_file_location('api_module', 'api.py')
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)

print("=== API Module Analysis ===")
print(f"Module file: {api_module.__file__}")
print(f"App title: {api_module.app.title}")
print(f"App version: {api_module.app.version}")
print("Routes:")
for route in api_module.app.routes:
    print(f"  - {route.path} ({route.methods})")

# Test the root endpoint directly
import asyncio
import json

async def test_root():
    from fastapi.testclient import TestClient
    client = TestClient(api_module.app)
    response = client.get("/")
    print(f"\n=== Root Endpoint Test ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_root())