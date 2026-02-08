import requests

BASE_URL = "http://localhost:8000"

# Test chat endpoint
response = requests.post(f"{BASE_URL}/chat", json={
    "message": "give me a video clip where scene changes first?",
    "video_id": None
})
print(response.json())
