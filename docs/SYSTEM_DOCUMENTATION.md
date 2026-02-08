# MOSAIC - Multimodal Video Understanding & Search System

> **System Documentation**  
> **Version:** 1.0  
> **Last Updated:** 2026-01-15

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [MCP Server Tools](#mcp-server-tools)
5. [Video Processing Pipeline](#video-processing-pipeline)
6. [Search Capabilities](#search-capabilities)
7. [API Endpoints](#api-endpoints)
8. [Agent System](#agent-system)
9. [Data Storage](#data-storage)
10. [Configuration](#configuration)
11. [Workflow Examples](#workflow-examples)

---

## 🎯 System Overview

**MOSAIC** (Multimodal Orchestration System for AI-powered Content) is an intelligent video understanding and search platform that enables natural language querying of video content. It combines:

- **Video Processing**: Frame extraction, audio transcription, image captioning
- **Multimodal Search**: Text, visual, and semantic search across video content
- **AI Agent**: LangChain-based ReAct agent for natural language interaction
- **Clip Generation**: Automatic video clip extraction based on search results

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Transcript Search** | Find spoken content using text queries |
| **Visual Search** | Find frames using CLIP visual-semantic similarity |
| **Caption Search** | Search AI-generated frame descriptions |
| **Clip Generation** | Extract video clips from search results |
| **Summarization** | Generate video content summaries |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MOSAIC Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐      ┌──────────────────┐      ┌───────────────────┐   │
│  │   mosaic-ui     │      │   mosaic-api     │      │   mosaic-mcp      │   │
│  │   (Next.js)     │ ───► │   (FastAPI)      │ ───► │   (FastMCP)       │   │
│  │                 │      │                  │      │                   │   │
│  │  ┌───────────┐  │      │  ┌────────────┐  │      │  ┌─────────────┐  │   │
│  │  │ Chat UI   │  │      │  │ VideoAgent │  │      │  │ VideoProc   │  │   │
│  │  │           │  │      │  │ (LangChain)│  │      │  │ Pipeline    │  │   │
│  │  └───────────┘  │      │  └────────────┘  │      │  └─────────────┘  │   │
│  │                 │      │        │         │      │        │          │   │
│  │  ┌───────────┐  │      │  ┌────────────┐  │      │  ┌─────────────┐  │   │
│  │  │ Video     │  │      │  │ MCPClient  │──┼──────┼─►│ SearchEngine│  │   │
│  │  │ Library   │  │      │  │            │  │      │  │             │  │   │
│  │  └───────────┘  │      │  └────────────┘  │      │  └─────────────┘  │   │
│  │                 │      │                  │      │        │          │   │
│  │  ┌───────────┐  │      │  ┌────────────┐  │      │  ┌─────────────┐  │   │
│  │  │ Upload    │  │      │  │ REST API   │  │      │  │ FAISS +     │  │   │
│  │  │ Interface │  │      │  │ Routes     │  │      │  │ ChromaDB    │  │   │
│  │  └───────────┘  │      │  └────────────┘  │      │  └─────────────┘  │   │
│  │                 │      │                  │      │                   │   │
│  └─────────────────┘      └──────────────────┘      └───────────────────┘   │
│                                                                              │
│       Port: 3000               Port: 8000              Port: 9090           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Communication

```
User Query → mosaic-ui → mosaic-api (Agent) → mosaic-mcp (Tools) → Vector DBs
                                    ↓
                              Search Results
                                    ↓
                            Clip Generation
                                    ↓
                          Response to User
```

---

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Next.js 15, React 19, TypeScript | Web interface |
| **API Server** | FastAPI, Uvicorn, Python 3.11+ | REST API, Agent hosting |
| **MCP Server** | FastMCP, Python | Tool server (MCP protocol) |
| **LLM Framework** | LangChain | Agent orchestration |

### AI/ML Models

| Model | Provider | Purpose |
|-------|----------|---------|
| `mistral-large-latest` | Mistral AI | LLM for agent reasoning |
| `whisper-large-v3-turbo` | Groq | Audio transcription |
| `llama-4-maverick-17b-128e-instruct` | Groq (Vision) | Image captioning |
| `clip-ViT-B-32` | SentenceTransformers | Image embeddings |
| `all-MiniLM-L6-v2` | SentenceTransformers | Text embeddings |

### Storage & Databases

| Storage | Technology | Purpose |
|---------|------------|---------|
| **Image Embeddings** | FAISS (IndexFlatL2) | Fast visual similarity search |
| **Text Embeddings** | ChromaDB | Transcript & caption search |
| **Files** | Local filesystem | Frames, audio, clips |

### External Dependencies

| Tool | Purpose |
|------|---------|
| **FFmpeg** | Video/audio processing, frame extraction, clip generation |
| **FFprobe** | Video metadata extraction |

---

## 🔧 MCP Server Tools

The MCP server exposes 9 tools via HTTP endpoints at `http://localhost:9090/mcp/v1/tools/`

### Tool 1: `process_video`

**Purpose**: Process and index a video file for search.

```python
# Endpoint: POST /mcp/v1/tools/process_video
{
    "video_path": "/path/to/video.mp4",
    "video_id": "unique_id"
}

# Returns
{
    "status": "success",
    "video_id": "unique_id",
    "frames_extracted": 150,
    "frames_captioned": 150,
    "transcript_length": 5000,
    "segments_count": 45,
    "transcript": "Full transcript text...",
    "faiss_index_path": "/storage/unique_id/faiss_index.bin",
    "vision_model_used": "meta-llama/llama-4-maverick-17b-128e-instruct"
}
```

**Processing Steps**:
1. Extract keyframes (1 in every 10 frames) using FFmpeg
2. Extract audio and transcribe with Groq Whisper
3. Generate CLIP embeddings for frames
4. Store image embeddings in FAISS
5. Generate AI captions for frames (1 in every 10)
6. Store transcripts and captions in ChromaDB

---

### Tool 2: `search_text`

**Purpose**: Search video transcript using text query.

```python
# Endpoint: POST /mcp/v1/tools/search_text
{
    "query": "neural networks explained",
    "video_id": "video_001",
    "k": 5
}

# Returns
[
    {
        "text": "Let me explain how neural networks work...",
        "start": 45.2,
        "end": 52.8,
        "distance": 0.234
    }
]
```

---

### Tool 3: `search_image`

**Purpose**: Search frames using image similarity (CLIP embeddings).

```python
# Endpoint: POST /mcp/v1/tools/search_image
{
    "query_image_path": "/path/to/query_image.jpg",
    "video_id": "video_001",
    "k": 5,
    "fps": 30.0
}

# Returns
[
    {
        "frame_path": "/storage/video_001/frames/frame_0045.jpg",
        "distance": 0.156,
        "frame_index": 45,
        "timestamp": 15.0,
        "clip_start": 14.0,
        "clip_duration": 5.0
    }
]
```

---

### Tool 4: `search_caption`

**Purpose**: Search frames using AI-generated captions.

```python
# Endpoint: POST /mcp/v1/tools/search_caption
{
    "query": "person holding a phone",
    "video_id": "video_001",
    "k": 5,
    "fps": 30.0
}

# Returns
[
    {
        "caption": "A person in a blue shirt holding a smartphone...",
        "frame_path": "/storage/video_001/frames/frame_0120.jpg",
        "frame_index": 120,
        "distance": 0.189,
        "timestamp": 40.0,
        "clip_start": 39.0,
        "clip_duration": 5.0
    }
]
```

---

### Tool 5: `search_visual`

**Purpose**: Search frames using CLIP visual-semantic embeddings (text-to-image).

```python
# Endpoint: POST /mcp/v1/tools/search_visual
{
    "query": "sunset over mountains",
    "video_id": "video_001",
    "k": 5,
    "fps": 30.0
}

# Returns
[
    {
        "frame_path": "/storage/video_001/frames/frame_0200.jpg",
        "distance": 0.342,
        "frame_index": 200,
        "timestamp": 66.67,
        "clip_start": 65.67,
        "clip_duration": 5.0,
        "search_type": "visual_clip"
    }
]
```

**Difference from `search_caption`**:
- `search_caption`: Searches text descriptions of frames
- `search_visual`: Uses CLIP to find visually similar content directly

---

### Tool 6: `generate_clips`

**Purpose**: Extract video clips based on search results.

```python
# Endpoint: POST /mcp/v1/tools/generate_clips
{
    "video_path": "/path/to/video.mp4",
    "hits": [
        {"start": 10.0, "end": 15.0},
        {"timestamp": 45.0}
    ],
    "output_dir": "/clips/video_001",
    "prefix": "clip"
}

# Returns
{
    "status": "success",
    "clips_generated": 2,
    "clip_paths": [
        "/clips/video_001/clip_1.mp4",
        "/clips/video_001/clip_2.mp4"
    ],
    "output_dir": "/clips/video_001"
}
```

---

### Tool 7: `get_video_info`

**Purpose**: Get information about a processed video.

```python
# Endpoint: POST /mcp/v1/tools/get_video_info
{
    "video_id": "video_001"
}

# Returns
{
    "status": "found",
    "video_id": "video_001",
    "frame_count": 150,
    "faiss_index_exists": true,
    "transcript_collection": "video_video_001",
    "frames_collection": "frames_video_001",
    "storage_path": "/storage/video_001",
    "video_path": "/uploads/video_001_myvideo.mp4"
}
```

---

### Tool 8: `list_videos`

**Purpose**: List all processed videos.

```python
# Endpoint: POST /mcp/v1/tools/list_videos
{}

# Returns
{
    "status": "success",
    "videos": [
        {"video_id": "video_001", "indexed": true, "frame_count": 150},
        {"video_id": "video_002", "indexed": true, "frame_count": 200}
    ],
    "count": 2
}
```

---

### Tool 9: `summarize_video`

**Purpose**: Generate a summary of video content from transcript.

```python
# Endpoint: POST /mcp/v1/tools/summarize_video
{
    "video_id": "video_001",
    "max_length": 150
}

# Returns
{
    "status": "success",
    "video_id": "video_001",
    "summary": "This video discusses the fundamentals of machine learning..."
}
```

---

## 🎬 Video Processing Pipeline

### Processing Flow

```
Video File
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    VideoProcessingPipeline                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Frame Extraction (FFmpeg)                          │
│  ├── Extract 1 in every 10 frames                           │
│  ├── Save as JPEG files                                     │
│  └── Calculate timestamps                                   │
│                                                              │
│  Step 2: Audio Extraction & Transcription                   │
│  ├── Extract audio track (WAV, 16kHz, mono)                 │
│  ├── Transcribe with Groq Whisper                           │
│  └── Get segment timestamps                                 │
│                                                              │
│  Step 3: Image Embeddings                                   │
│  ├── Generate CLIP embeddings for all frames                │
│  └── Store in FAISS index                                   │
│                                                              │
│  Step 4: Transcript Storage                                 │
│  ├── Generate text embeddings                               │
│  └── Store in ChromaDB (collection: video_{id})             │
│                                                              │
│  Step 5: Frame Captioning                                   │
│  ├── Caption 1 in every 10 frames with Vision model         │
│  └── Propagate captions to surrounding frames               │
│                                                              │
│  Step 6: Caption Storage                                    │
│  ├── Generate text embeddings for captions                  │
│  └── Store in ChromaDB (collection: frames_{id})            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Frame Extraction Details

- **Method**: FFmpeg with select filter `select='not(mod(n,10))'`
- **Frame Rate**: Extracts every 10th frame
- **Output Format**: JPEG with quality level 2
- **Naming**: `frame_0001.jpg`, `frame_0002.jpg`, ...

### Captioning Strategy

- Only 1 in every 10 extracted frames is captioned (saves API calls)
- Surrounding frames inherit the nearest captioned frame's description
- Rate limiting: 0.5s delay between API calls

---

## 🔍 Search Capabilities

### Search Methods Comparison

| Method | Query Type | Index Used | Best For |
|--------|------------|------------|----------|
| `search_text` | Text | ChromaDB | Finding spoken content |
| `search_visual` | Text | FAISS (CLIP) | Visual similarity to text description |
| `search_caption` | Text | ChromaDB | Finding described scenes |
| `search_image` | Image | FAISS (CLIP) | Finding similar frames to reference image |

### Search Result Structure

All search methods return timing information for clip generation:

```python
{
    # Core result data
    "text" / "caption" / "frame_path": "...",
    "distance": 0.234,  # Lower = more similar
    
    # Timing for clip generation
    "timestamp": 45.5,      # Frame timestamp in seconds
    "start": 45.0,          # Transcript segment start (text search)
    "end": 52.0,            # Transcript segment end (text search)
    "clip_start": 44.5,     # Suggested clip start (1s before)
    "clip_duration": 5.0    # Default clip duration
}
```

---

## 🌐 API Endpoints

### FastAPI Backend (Port 8000)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Health check |
| `POST` | `/upload-video` | Upload and process video |
| `GET` | `/status/{task_id}` | Get processing status |
| `POST` | `/chat` | Chat with video agent |
| `POST` | `/reset-memory` | Clear agent memory |
| `GET` | `/videos` | List all videos |
| `GET` | `/videos/{video_id}` | Get video info |
| `GET` | `/clips/{filename}` | Serve video clips |

### Request/Response Examples

#### Upload Video
```http
POST /upload-video
Content-Type: multipart/form-data

file: <video.mp4>

Response:
{
    "status": "accepted",
    "video_id": "abc12345",
    "task_id": "uuid-here",
    "message": "Video uploaded successfully. Processing in background."
}
```

#### Chat with Agent
```http
POST /chat
Content-Type: application/json

{
    "message": "Find moments where someone talks about AI",
    "video_id": "abc12345"
}

Response:
{
    "response": "I found 3 moments discussing AI...",
    "video_id": "abc12345",
    "metadata": {"success": true}
}
```

---

## 🤖 Agent System

### VideoAgent Overview

The agent uses LangChain's ReAct (Reasoning + Acting) pattern with custom tools.

### Agent Tools

| Tool Name | Description | Input Format |
|-----------|-------------|--------------|
| `search_transcript` | Search spoken content | `'query\|video_id'` |
| `search_frames` | Search by caption | `'description\|video_id'` |
| `search_visual` | CLIP visual search | `'description\|video_id'` |
| `get_video_info` | Get video metadata | `'video_id'` |
| `list_videos` | List all videos | `(no input)` |
| `generate_clips` | Create video clips | `'video_id\|[hits_json]'` |
| `summarize_video` | Get video summary | `'video_id'` |

### Agent Prompt Template

```
You are a helpful video analysis assistant. You can search videos and generate clips.

WORKFLOW FOR COMMON TASKS:
1. Finding spoken content: Use search_transcript
2. Finding visual scenes (by caption): Use search_frames  
3. Finding visual scenes (by visual similarity): Use search_visual
4. Getting clips: FIRST search, THEN use generate_clips with results
5. Summarizing: Use summarize_video

FORMAT:
Thought: <reasoning>
Action: <tool_name>
Action Input: <input>

OR

Thought: I now know the final answer
Final Answer: <answer>
```

---

## 💾 Data Storage

### Directory Structure

```
storage/
├── {video_id}/
│   ├── frames/
│   │   ├── frame_0001.jpg
│   │   ├── frame_0002.jpg
│   │   └── ...
│   ├── audio.wav
│   ├── faiss_index.bin
│   ├── frame_timestamps.json
│   ├── frame_captions.json
│   └── video_info.json

chroma_db/
├── video_{video_id}/        # Transcript collection
└── frames_{video_id}/       # Caption collection

clips_output/
├── {video_id}/
│   ├── clip_1.mp4
│   ├── clip_2.mp4
│   └── ...
```

### FAISS Index

- **Index Type**: `IndexFlatL2` (Euclidean distance)
- **Dimension**: 512 (CLIP embedding size)
- **File**: `faiss_index.bin`

### ChromaDB Collections

**Transcript Collection** (`video_{video_id}`):
```python
{
    "documents": ["transcript segment text"],
    "embeddings": [...],  # 384-dim MiniLM
    "metadatas": [{
        "type": "transcript_segment",
        "video_id": "...",
        "start": 10.5,
        "end": 15.2
    }]
}
```

**Caption Collection** (`frames_{video_id}`):
```python
{
    "documents": ["A person standing near a whiteboard..."],
    "embeddings": [...],  # 384-dim MiniLM
    "metadatas": [{
        "type": "frame",
        "video_id": "...",
        "frame_path": "...",
        "frame_index": 45,
        "timestamp": 15.0,
        "caption": "..."
    }]
}
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required API Keys
GROQ_API_KEY=gsk_xxxxx           # Groq API for Whisper & Vision
MISTRAL_API_KEY=xxxxx            # Mistral AI for LLM

# Optional (alternative LLMs)
GEMINI_API_KEY=xxxxx             # Google Gemini

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
MCP_SERVER_URL=http://127.0.0.1:9090

# Storage
STORAGE_DIR=./storage/frames
UPLOAD_DIR=./storage/uploads

# Models
VISION_MODEL=meta-llama/llama-4-maverick-17b-128e-instruct
```

### Python Dependencies

**mosaic-api**:
- fastapi, uvicorn
- langchain, langchain-core, langchain-community
- langchain-groq, langchain-mistralai
- pydantic, httpx, requests

**mosaic-mcp**:
- mcp, fastmcp
- sentence-transformers
- chromadb, faiss-cpu
- groq, Pillow, numpy

---

## 📋 Workflow Examples

### Example 1: Upload and Process Video

```
User: Upload video "presentation.mp4"

1. POST /upload-video with file
2. API returns task_id
3. Background: MCP server processes video
   - Extracts 150 frames
   - Transcribes 10 minutes of audio
   - Generates 15 AI captions
   - Stores all embeddings
4. GET /status/{task_id} → "completed"
```

### Example 2: Natural Language Search

```
User: "Show me where the speaker talks about neural networks"

Agent Process:
1. Thought: I need to search the transcript for "neural networks"
2. Action: search_transcript
3. Action Input: neural networks|video_001
4. Observation: Found 3 matches at 2:30, 5:45, 8:12
5. Final Answer: "I found 3 moments where neural networks are discussed..."
```

### Example 3: Visual Search with Clip Generation

```
User: "Find frames showing a red car and create clips"

Agent Process:
1. Thought: I should use visual search to find red car frames
2. Action: search_visual
3. Action Input: red car|video_001
4. Observation: [{"timestamp": 45.2, ...}, {"timestamp": 78.5, ...}]
5. Thought: Now I'll generate clips from these results
6. Action: generate_clips
7. Action Input: video_001|[{"timestamp": 45.2, ...}]
8. Observation: {"clips_generated": 2, "clip_paths": [...]}
9. Final Answer: "I found 2 frames with a red car and generated clips..."
```

---

## 🚀 Quick Start

```bash
# Terminal 1: Start MCP Server
cd mosaic/mosaic-mcp
python src/server.py --port 9090

# Terminal 2: Start API Server
cd mosaic/mosaic-api/app
python api.py

# Terminal 3: Start Frontend
cd mosaic/mosaic-ui
npm run dev
```

**Access Points**:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- MCP Server: http://localhost:9090

---

*This documentation covers the complete MOSAIC system architecture, tools, and workflows.*
