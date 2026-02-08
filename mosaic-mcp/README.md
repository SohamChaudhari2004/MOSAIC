# 🎬 MOSAIC MCP Server

FastMCP server for video processing, embedding generation, and intelligent search.

## 📋 Overview

The `mosaic-mcp` is the Model Context Protocol server that provides:
- Video frame extraction and processing
- Audio transcription using Whisper
- Image captioning with vision models
- Vector embeddings (CLIP + text models)
- FAISS and ChromaDB vector search
- Video clip generation
- Multi-modal search capabilities

## 🏗️ Architecture

```
mosaic-mcp/
├── src/
│   ├── server.py            # FastMCP server
│   ├── video_processor.py   # Video processing pipeline
│   ├── search_engine.py     # Vector search engine
│   └── chroma_db/           # ChromaDB storage
├── tests/                   # Test suite
├── Dockerfile               # Docker build configuration
├── requirements.txt         # Python dependencies
└── pyproject.toml           # Project configuration
```

## 🔧 Technology Stack

### Core Technologies
- **FastMCP** - Model Context Protocol server
- **FFmpeg** - Video/audio processing
- **OpenCV** - Computer vision

### AI Models
- **CLIP (ViT-B-32)** - Visual-semantic embeddings
- **Whisper Large V3 Turbo** - Audio transcription (Groq)
- **Llama 4 Maverick** - Image captioning (Groq)
- **all-MiniLM-L6-v2** - Text embeddings

### Vector Databases
- **FAISS** - Fast similarity search for images
- **ChromaDB** - Persistent vector database for text

## 📦 Installation

### Using Docker (Recommended)

```bash
# From root directory
docker-compose up mcp-server

# Or build separately
cd mosaic-mcp
docker build -t mosaic-mcp .
docker run -p 9090:9090 --env-file ../.env mosaic-mcp
```

### Local Development

```bash
cd mosaic-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install ffmpeg libsm6 libxext6

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example ../.env
# Edit .env with your API keys

# Run the server
python src/server.py
```

## 🔌 MCP Tools

The server exposes 9 tools via HTTP at `http://localhost:9090/mcp/v1/tools/`:

### 1. process_video

Process and index a video file for search.

```python
{
    "video_path": "/path/to/video.mp4",
    "video_id": "unique_id"
}
```

**Pipeline:**
1. Extract frames (1 per second)
2. Transcribe audio with Whisper
3. Generate image captions
4. Create CLIP embeddings
5. Index in FAISS and ChromaDB

### 2. search_transcript

Search transcribed audio content.

```python
{
    "query": "artificial intelligence",
    "video_id": "unique_id",
    "top_k": 5
}
```

Returns timestamped transcript segments matching the query.

### 3. search_visual

CLIP-based visual similarity search.

```python
{
    "query": "person wearing red shirt",
    "video_id": "unique_id",
    "top_k": 5
}
```

Returns frames with highest visual-semantic similarity.

### 4. search_caption

Search AI-generated frame descriptions.

```python
{
    "query": "sunset over mountains",
    "video_id": "unique_id",
    "top_k": 5
}
```

Returns frames matching caption descriptions.

### 5. get_transcript

Retrieve complete video transcript.

```python
{
    "video_id": "unique_id"
}
```

Returns full transcript with timestamps.

### 6. get_video_metadata

Get video information and processing status.

```python
{
    "video_id": "unique_id"
}
```

Returns duration, frame count, transcript status, etc.

### 7. list_videos

List all processed videos.

```python
{}
```

Returns array of video metadata.

### 8. generate_clip

Extract video segment.

```python
{
    "video_id": "unique_id",
    "start_time": 120.5,
    "end_time": 145.0,
    "output_name": "highlight.mp4"
}
```

Generates MP4 clip using FFmpeg.

### 9. summarize_video

Generate content summary.

```python
{
    "video_id": "unique_id"
}
```

Returns AI-generated summary of video content.

## 🎥 Video Processing Pipeline

### Frame Extraction

```python
# Extract 1 frame per second
ffmpeg -i input.mp4 -vf fps=1 frame_%04d.jpg
```

**Configuration:**
- Frame rate: 1 fps (configurable)
- Format: JPEG
- Resolution: Original (can be resized)

### Audio Transcription

```python
# Groq Whisper API
transcription = groq.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3-turbo",
    response_format="verbose_json",
    timestamp_granularities=["segment"]
)
```

**Features:**
- Word-level timestamps
- Speaker diarization support
- Multiple language support
- High accuracy (Whisper v3)

### Image Captioning

```python
# Groq Vision API
caption = groq.chat.completions.create(
    model="llama-4-maverick-17b-128e-instruct",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    }]
)
```

**Output:**
- Detailed scene descriptions
- Object identification
- Action detection

### Embedding Generation

#### CLIP Embeddings (Images)
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('clip-ViT-B-32')
embeddings = model.encode(images)
```

**Dimensions:** 512
**Index:** FAISS (IndexFlatL2)

#### Text Embeddings
```python
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)
```

**Dimensions:** 384
**Database:** ChromaDB

## 🔍 Search Engine

### FAISS Visual Search

```python
class SearchEngine:
    def search_visual(self, query_text, top_k=5):
        # Encode query with CLIP
        query_embedding = self.clip_model.encode([query_text])
        
        # Search FAISS index
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        
        return results
```

**Performance:**
- ~0.1ms per query
- Handles millions of vectors
- GPU acceleration support

### ChromaDB Text Search

```python
results = collection.query(
    query_texts=[query],
    n_results=top_k,
    where={"video_id": video_id}
)
```

**Features:**
- Persistent storage
- Metadata filtering
- Automatic embedding generation

## 📊 Data Storage

### Directory Structure

```
storage/
├── frames/
│   └── {video_id}/
│       ├── frame_0001.jpg
│       ├── frame_0002.jpg
│       └── ...
├── chroma_db/
│   └── {collections}/
├── faiss_indices/
│   └── {video_id}.index
└── metadata/
    └── {video_id}.json
```

### Metadata Format

```json
{
    "video_id": "abc123",
    "filename": "video.mp4",
    "duration": 120.5,
    "frame_count": 120,
    "fps": 1,
    "transcript": [...],
    "captions": [...],
    "processed_at": "2026-02-08T12:00:00Z"
}
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_video_processor.py -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html

# Integration tests
pytest tests/test_tools.py -v -m integration
```

## ⚙️ Configuration

### Environment Variables

```bash
# API Keys
GROQ_API_KEY=your_groq_key

# Processing Settings
FRAME_RATE=1
BATCH_SIZE=32
MAX_FILE_SIZE=1000000000

# Model Settings
EMBEDDING_MODEL=clip-ViT-B-32
TEXT_EMBEDDING_MODEL=all-MiniLM-L6-v2
WHISPER_MODEL=whisper-large-v3-turbo
VISION_MODEL=llama-4-maverick-17b-128e-instruct

# Storage
STORAGE_PATH=./storage
CHROMA_PERSIST_DIRECTORY=./src/chroma_db

# Logging
LOG_LEVEL=INFO
```

## 🚀 Performance Optimization

### FAISS GPU Acceleration

```python
# Use GPU for faster search
import faiss
faiss_index = faiss.index_cpu_to_gpu(
    faiss.StandardGpuResources(),
    0,  # GPU ID
    cpu_index
)
```

### Batch Processing

```python
# Process frames in batches
for batch in chunks(frames, batch_size=32):
    embeddings = model.encode(batch)
    faiss_index.add(embeddings)
```

### Caching

```python
# Cache model predictions
@lru_cache(maxsize=1000)
def get_caption(frame_path):
    return caption_model.predict(frame_path)
```

## 🐛 Debugging

### Enable Verbose Logging

```python
# src/server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test video processor
from src.video_processor import VideoProcessor
processor = VideoProcessor()
frames = processor.extract_frames("test.mp4")

# Test search engine
from src.search_engine import SearchEngine
engine = SearchEngine()
results = engine.search_visual("cat", top_k=5)
```

### Check Model Loading

```python
# Verify models are loaded
python -c "from sentence_transformers import SentenceTransformer; \
           model = SentenceTransformer('clip-ViT-B-32'); \
           print('CLIP loaded successfully')"
```

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:9090/health
```

### Check Processing Status

```python
# Get video metadata
curl -X POST http://localhost:9090/mcp/v1/tools/get_video_metadata \
  -H "Content-Type: application/json" \
  -d '{"video_id": "abc123"}'
```

## 🛠️ Development

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

### Add New Tool

```python
# src/server.py
@mcp.tool()
async def my_new_tool(video_id: str) -> dict:
    """Tool description"""
    # Implementation
    return {"result": "success"}
```

## 🤝 Contributing

1. Add tests for new features
2. Update documentation
3. Follow code style guidelines
4. Test with real videos

## 📞 Troubleshooting

### FFmpeg Not Found
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
# Windows: Download from https://ffmpeg.org/
```

### Model Download Fails
```bash
# Models auto-download on first use
# Check internet connection and disk space

# Manual download
python -c "from sentence_transformers import SentenceTransformer; \
           SentenceTransformer('clip-ViT-B-32')"
```

### Out of Memory
```bash
# Reduce batch size
BATCH_SIZE=16

# Use CPU-only FAISS
pip uninstall faiss-gpu
pip install faiss-cpu
```

### Groq API Errors
```bash
# Check API key
echo $GROQ_API_KEY

# Check rate limits
# Groq has generous free tier limits
```

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Part of MOSAIC** - [Back to main project](../README.md)
