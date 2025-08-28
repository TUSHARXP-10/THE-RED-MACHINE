#!/usr/bin/env python3
import requests
import json

def test_server():
    base_url = "http://localhost:8002"
    
    print("Testing server endpoints...")
    
    try:
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Root response: {response.json()}")
        else:
            print(f"Root error: {response.text}")
            
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
            
        # Test OpenAPI schema
        print("\nTesting OpenAPI schema...")
        response = requests.get(f"{base_url}/openapi.json")
        print(f"OpenAPI status: {response.status_code}")
        if response.status_code == 200:
            schema = response.json()
            print(f"API Title: {schema.get('info', {}).get('title', 'Unknown')}")
            print(f"API Version: {schema.get('info', {}).get('version', 'Unknown')}")
            print(f"Available paths: {list(schema.get('paths', {}).keys())}")
            
    except requests.exceptions.ConnectionError:
        print("Server is not running")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_server()