# 🚀 MOSAIC API Server

FastAPI backend for MOSAIC - LangChain agent orchestration and REST API endpoints.

## 📋 Overview

The `mosaic-api` is the core backend service that handles:

- REST API endpoints for video management
- LangChain ReAct agent for intelligent query processing
- MCP (Model Context Protocol) client integration
- Chat interface and conversation management
- Video upload and metadata storage

## 🏗️ Architecture

```
mosaic-api/
├── app/
│   ├── api.py           # FastAPI routes and endpoints
│   ├── agent.py         # LangChain ReAct agent
│   ├── mcp_client.py    # MCP client for tool calls
│   ├── config.py        # Configuration settings
│   └── schemas.py       # Pydantic data models
├── tests/               # Test suite
├── Dockerfile           # Docker build configuration
├── requirements.txt     # Python dependencies
└── pyproject.toml       # Project configuration
```

## 🔧 Technology Stack

- **FastAPI** - Modern Python web framework
- **LangChain** - LLM orchestration and agent framework
- **Mistral AI** - Large language model for reasoning
- **MCP Client** - Tool calling via Model Context Protocol
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and serialization

## 📦 Installation

### Using Docker (Recommended)

```bash
# From root directory
docker-compose up api-server

# Or build separately
cd mosaic-api
docker build -t mosaic-api .
docker run -p 8000:8000 --env-file ../.env mosaic-api
```

### Local Development

```bash
cd mosaic-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example ../.env
# Edit .env with your API keys

# Run the server
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### Videos

- `POST /api/videos/upload` - Upload a new video file
- `GET /api/videos` - List all uploaded videos
- `GET /api/videos/{video_id}` - Get video details
- `POST /api/videos/{video_id}/process` - Process video for analysis
- `DELETE /api/videos/{video_id}` - Delete video and associated data

### Search

- `POST /api/search/transcript` - Search in audio transcripts
- `POST /api/search/visual` - Visual similarity search using CLIP
- `POST /api/search/caption` - Search in AI-generated captions
- `POST /api/search/combined` - Multi-modal search

### Chat & Agent

- `POST /api/chat` - Send message to LangChain agent
- `GET /api/chat/history` - Retrieve chat history
- `POST /api/chat/clear` - Clear conversation history

### Clips

- `POST /api/videos/{video_id}/clips` - Generate video clip
- `GET /api/clips` - List all generated clips
- `GET /api/clips/{clip_id}` - Download specific clip

### System

- `GET /health` - Health check endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🤖 LangChain Agent

The agent uses the **ReAct** (Reasoning + Acting) pattern:

```python
# Example agent workflow
User Query → Agent Reasoning → Tool Selection → Tool Execution → Response
```

### Available Tools (via MCP)

1. **process_video** - Process and index video
2. **search_transcript** - Search transcribed audio
3. **search_visual** - CLIP-based visual search
4. **search_caption** - Search image captions
5. **get_transcript** - Retrieve full transcript
6. **get_video_metadata** - Get video information
7. **list_videos** - List all indexed videos
8. **generate_clip** - Extract video segment
9. **summarize_video** - Generate content summary

## 📝 Configuration

### Environment Variables

Required in `.env` file:

```bash
# API Keys
MISTRAL_API_KEY=your_mistral_key

# Server Config
MCP_SERVER_URL=http://localhost:9090
API_PORT=8000

# Storage Paths
STORAGE_PATH=./storage
UPLOAD_PATH=./storage/uploads

# Logging
LOG_LEVEL=INFO
```

### Config File (`app/config.py`)

```python
class Settings(BaseSettings):
    mistral_api_key: str
    mcp_server_url: str = "http://localhost:9090"
    max_file_size: int = 1000000000  # 1GB
    allowed_extensions: list = [".mp4", ".avi", ".mov", ".mkv"]
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_video.py -v
```

## 🔌 MCP Client Integration

The MCP client communicates with the `mosaic-mcp` server:

```python
# app/mcp_client.py
class MCPClient:
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call MCP tool via HTTP"""
        response = await self.client.post(
            f"{self.base_url}/mcp/v1/tools/{tool_name}",
            json=arguments
        )
        return response.json()
```

## 📊 Data Models

### Video Schema

```python
class Video(BaseModel):
    id: str
    filename: str
    path: str
    size: int
    duration: float
    status: str  # "uploaded", "processing", "ready", "error"
    created_at: datetime
```

### Chat Message

```python
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    video_id: Optional[str]
```

### Search Result

```python
class SearchResult(BaseModel):
    frame_number: int
    timestamp: float
    score: float
    path: str
    metadata: dict
```

## 🚀 Usage Examples

### Upload Video

```bash
curl -X POST "http://localhost:8000/api/videos/upload" \
  -F "file=@video.mp4"
```

### Chat with Agent

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is discussed in the video?",
    "video_id": "abc123"
  }'
```

### Search Transcript

```bash
curl -X POST "http://localhost:8000/api/search/transcript" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "video_id": "abc123",
    "top_k": 5
  }'
```

## 🐛 Debugging

### Enable Debug Logging

```python
# app/api.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Agent Reasoning

```bash
# Set environment variable
LOG_LEVEL=DEBUG
```

### Test MCP Connection

```python
# Test script
from app.mcp_client import MCPClient

client = MCPClient()
result = await client.call_tool("list_videos", {})
print(result)
```

## 🔒 Security Considerations

- Validate file uploads (size, type)
- Sanitize user inputs
- Rate limiting (TODO)
- API authentication (TODO)
- CORS configuration

## 📈 Performance

- Async/await for I/O operations
- Connection pooling for MCP client
- Request timeout handling
- Streaming responses for large data

## 🛠️ Development

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

### Hot Reload

```bash
# Auto-reload on file changes
uvicorn app.api:app --reload
```

## 📚 API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update API documentation
4. Run linting before committing

## 📞 Troubleshooting

### MCP Server Connection Failed

```bash
# Check if MCP server is running
curl http://localhost:9090/health

# Check environment variable
echo $MCP_SERVER_URL
```

### File Upload Fails

```bash
# Check storage directory exists
mkdir -p storage/uploads

# Check permissions
chmod 755 storage/
```

### Agent Not Responding

```bash
# Verify API key
echo $MISTRAL_API_KEY

# Check logs
docker-compose logs api-server
```

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Part of MOSAIC** - [Back to main project](../README.md)
