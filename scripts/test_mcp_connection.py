"""Test script to verify MCP client connection"""
import requests
import json
import time

# Wait for servers to start
print("Waiting for servers to start...")
time.sleep(35)

# Test MCP server directly
print("\n1. Testing MCP server directly...")
url = "http://127.0.0.1:9090/mcp"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}
payload = {
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "tools/list"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test via API server
print("\n2. Testing via API server...")
api_url = "http://localhost:8000/videos"
try:
    response = requests.get(api_url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\nTest complete!")
