"""Direct test of MCP server to debug the 400 error"""
import requests
import json

url = "http://127.0.0.1:9090/mcp"

# Test 1: Initialize
print("=== Test 1: Initialize MCP Session ===")
init_request = {
    "jsonrpc": "2.0",
    "id": "init-1",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

try:
    response = requests.post(url, json=init_request, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    session_id = response.headers.get("mcp-session-id")
    print(f"\nSession ID: {session_id}")
    
    # Test 2: Send initialized notification
    if session_id and response.status_code == 200:
        print("\n=== Test 2: Send Initialized Notification ===")
        notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        headers["mcp-session-id"] = session_id
        response2 = requests.post(url, json=notif, headers=headers)
        print(f"Status: {response2.status_code}")
        
        # Test 3: List tools
        print("\n=== Test 3: List Tools ===")
        list_request = {
            "jsonrpc": "2.0",
            "id": "list-1",
            "method": "tools/list"
        }
        response3 = requests.post(url, json=list_request, headers=headers)
        print(f"Status: {response3.status_code}")
        print(f"Response: {json.dumps(response3.json(), indent=2)}")
        
        # Test 4: Call a tool
        print("\n=== Test 4: Call list_videos Tool ===")
        call_request = {
            "jsonrpc": "2.0",
            "id": "call-1",
            "method": "tools/call",
            "params": {
                "name": "list_videos",
                "arguments": {}
            }
        }
        response4 = requests.post(url, json=call_request, headers=headers)
        print(f"Status: {response4.status_code}")
        print(f"Response: {json.dumps(response4.json(), indent=2)}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
