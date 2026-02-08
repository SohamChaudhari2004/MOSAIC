# MOSAIC Video Analyzer - Project Structure

> **Last Updated:** 2026-01-15

This document provides a comprehensive overview of the MOSAIC Video Analyzer project structure, including all directories, files, and their purposes.

---

## 📁 Root Directory: `D:\Mosaic_video_analyzer`

```
Mosaic_video_analyzer/
├── .git/                           # Git version control
├── .gitignore                      # Git ignore rules
├── .vscode/                        # VS Code workspace settings
├── venv/                           # Python virtual environment
└── mosaic/                         # Main project directory
```

---

## 📁 Main Project: `mosaic/`

```
mosaic/
├── .env                            # Environment variables (API keys, secrets)
├── .env.example                    # Example environment file template
├── .gitignore                      # Git ignore rules for mosaic
├── LICENSE                         # Project license
├── Makefile                        # Build automation scripts
├── README.md                       # Project documentation
├── docker-compose.yml              # Docker orchestration config
├── docker-compose.dev.yml          # Docker dev environment config
├── package.json                    # Node.js dependencies (root level)
├── pyproject.toml                  # Python project configuration
│
├── .github/                        # GitHub specific files
│   └── workflows/                  # GitHub Actions CI/CD workflows
│
├── docs/                           # Documentation
│   ├── api-reference.md            # API documentation
│   ├── architecture.md             # System architecture docs
│   ├── deployment.md               # Deployment guide
│   └── user-guide.md               # User manual
│
├── scripts/                        # Utility scripts
│   ├── deploy.sh                   # Deployment script
│   ├── setup.sh                    # Setup script
│   ├── download_models.py          # ML models downloader
│   ├── embeddings.py               # Embeddings utility (723 bytes)
│   ├── test_audio.py               # Audio processing tests (1,080 bytes)
│   └── test_frame_extraction.py    # Frame extraction tests (1,838 bytes)
│
├── extracted_frames/               # Temporary extracted video frames
│
├── mosaic-api/                     # FastAPI Backend Service
├── mosaic-mcp/                     # MCP (Model Context Protocol) Server
└── mosaic-ui/                      # Next.js Frontend Application
```

---

## 🔧 Backend API: `mosaic-api/`

The FastAPI backend service that handles video uploads, agent orchestration, and API endpoints.

```
mosaic-api/
├── .dockerignore                   # Docker ignore rules
├── Dockerfile                      # Docker build configuration
├── README.md                       # API service documentation
├── poetry.lock                     # Poetry dependency lock file
├── pyproject.toml                  # Python project config
├── requirements.txt                # Python dependencies
│
├── app/                            # Main application code
│   ├── __init__.py                 # Python package init
│   ├── api.py                      # FastAPI routes & endpoints (5,160 bytes)
│   ├── agent.py                    # Video Agent implementation (14,259 bytes)
│   ├── config.py                   # Configuration settings (698 bytes)
│   ├── mcp_client.py               # MCP client for tool calls (2,604 bytes)
│   ├── schemas.py                  # Pydantic data models (644 bytes)
│   ├── test_api.py                 # API tests (249 bytes)
│   │
│   ├── __pycache__/                # Python bytecode cache
│   ├── clips_output/               # Video clips output directory
│   ├── uploads/                    # Video upload directory
│   │
│   └── storage/                    # Storage management
│       └── uploads/                # Uploaded files storage
│           └── video_paths.json    # Video path mappings
│
├── mosaic/                         # Additional mosaic modules
├── tests/                          # Test suite
└── uploads/                        # Upload staging directory
```

### Key API Files:

| File | Size | Purpose |
|------|------|---------|
| `api.py` | 5.16 KB | FastAPI application with routes for video upload, search, and chat |
| `agent.py` | 14.26 KB | LangChain-based Video Agent for orchestrating video analysis |
| `mcp_client.py` | 2.60 KB | Client for communicating with MCP server tools |
| `config.py` | 698 B | Environment-based configuration (API keys, paths) |
| `schemas.py` | 644 B | Pydantic models for request/response validation |

---

## 🛠️ MCP Server: `mosaic-mcp/`

The Model Context Protocol (MCP) server that provides video processing tools.

```
mosaic-mcp/
├── .dockerignore                   # Docker ignore rules
├── Dockerfile                      # Docker build configuration
├── README.md                       # MCP server documentation
├── fastmcp.json                    # FastMCP configuration
├── poetry.lock                     # Poetry dependency lock file
├── pyproject.toml                  # Python project config
├── requirements.txt                # Python dependencies (151 bytes)
│
├── src/                            # Source code
│   ├── server.py                   # Main MCP server (17,355 bytes)
│   ├── video_processor.py          # Video processing logic (18,910 bytes)
│   ├── search_engine.py            # Semantic search engine (12,643 bytes)
│   │
│   ├── __pycache__/                # Python bytecode cache
│   │
│   ├── chroma_db/                  # ChromaDB vector store
│   ├── clips_output/               # Processed video clips
│   │
│   ├── storage/                    # Storage directories
│   │   └── frames/                 # Extracted video frames
│   │
│   ├── mosaic/                     # Mosaic-specific modules
│   │   └── extracted_frames/       # Frame extraction output
│   │
│   ├── server_log_2.txt            # Server logs (224 bytes)
│   └── server_err_2.txt            # Server error logs (2,203 bytes)
│
└── tests/                          # Test suite
```

### Key MCP Files:

| File | Size | Purpose |
|------|------|---------|
| `server.py` | 17.35 KB | FastMCP server with video processing tools (extract frames, transcribe, embed, search) |
| `video_processor.py` | 18.91 KB | FFmpeg-based video processing (frame extraction, audio extraction, clip creation) |
| `search_engine.py` | 12.64 KB | ChromaDB-powered semantic search for video content |

### MCP Tools to be Exposed:

1. **`extract_frames`** - Extract keyframes from video
2. **`transcribe_audio`** - Transcribe video audio using Whisper
3. **`Caption image frames(1 in 20 frames)`** - caption Images using Blip
4. **`generate_embeddings`** - Create semantic embeddings for text/images
5. **`search_content`** - Semantic search across video content
6. **`create_clip`** - Extract video clips based on timestamps

---

## 🎨 Frontend UI: `mosaic-ui/`

The Next.js frontend application with a HAL 9000-inspired design.

```
mosaic-ui/
├── .gitignore                      # Git ignore rules (480 bytes)
├── .next/                          # Next.js build output (auto-generated)
├── node_modules/                   # Node.js dependencies
│
├── Dockerfile                      # Docker build configuration (1,710 bytes)
├── README.md                       # Frontend documentation (1,450 bytes)
├── next.config.ts                  # Next.js configuration (133 bytes)
├── next-env.d.ts                   # Next.js TypeScript declarations
├── tsconfig.json                   # TypeScript configuration (666 bytes)
├── eslint.config.mjs               # ESLint configuration (465 bytes)
├── postcss.config.mjs              # PostCSS configuration (94 bytes)
├── package.json                    # Node.js dependencies (675 bytes)
├── package-lock.json               # Dependency lock file (160 KB)
│
├── app/                            # Next.js App Router pages
│   ├── favicon.ico                 # Application favicon
│   ├── globals.css                 # Global styles (884 bytes)
│   ├── layout.tsx                  # Root layout component (704 bytes)
│   └── page.tsx                    # Main page component (4,295 bytes)
│
├── components/                     # React components
│   ├── ChatArea.tsx                # Chat interface component (4,798 bytes)
│   └── Sidebar.tsx                 # Sidebar navigation (2,862 bytes)
│
├── lib/                            # Utility libraries
│   └── api.ts                      # API client functions (1,334 bytes)
│
└── public/                         # Static assets
    ├── file.svg                    # File icon
    ├── globe.svg                   # Globe icon
    ├── next.svg                    # Next.js logo
    ├── vercel.svg                  # Vercel logo
    └── window.svg                  # Window icon
```

### Key UI Files:

| File | Size | Purpose |
|------|------|---------|
| `page.tsx` | 4.30 KB | Main application page with video library and chat |
| `ChatArea.tsx` | 4.80 KB | Chat interface for video search queries |
| `Sidebar.tsx` | 2.86 KB | Sidebar with video library and navigation |
| `api.ts` | 1.33 KB | API client for backend communication |
| `globals.css` | 884 B | Global styles and CSS variables |

---

## 📦 Dependencies

### Python Dependencies (`mosaic-api/requirements.txt`)

```
fastapi
uvicorn[standard]
langchain
langchain-groq
pydantic
python-multipart
httpx
python-dotenv
requests
```

### Python Dependencies (`mosaic-mcp/requirements.txt`)

```
(See file for complete list)
```

### Node.js Dependencies (`mosaic-ui/package.json`)

Core dependencies include:
- Next.js 15+
- React 19+
- TypeScript
- TailwindCSS (if configured)

---

## 🔑 Environment Variables

Required in `.env` file:

```env
# API Keys
GROQ_API_KEY=          # Groq LLM API key
OPENAI_API_KEY=        # OpenAI API key (for embeddings)

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
MCP_SERVER_URL=http://localhost:5001

# Paths
UPLOAD_DIR=./uploads
FRAMES_DIR=./storage/frames
CLIPS_DIR=./clips_output
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOSAIC Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│    │   mosaic-ui  │ ──▶  │  mosaic-api  │ ──▶  │  mosaic-mcp  │ │
│    │   (Next.js)  │      │  (FastAPI)   │      │  (FastMCP)   │ │
│    │              │      │              │      │              │ │
│    │  - Chat UI   │      │  - Agent     │      │  - FFmpeg    │ │
│    │  - Video     │      │  - Routes    │      │  - Whisper   │ │
│    │    Library   │      │  - MCP Client│      │  - ChromaDB  │ │
│    └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                                  │
│    Port: 3000             Port: 8000           Port: 5001       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 File Statistics

| Service | Files | Directories | Total Code Size |
|---------|-------|-------------|-----------------|
| mosaic-api | 7 | 4 | ~23 KB |
| mosaic-mcp | 5 | 5 | ~49 KB |
| mosaic-ui | 7 | 6 | ~13 KB |
| docs | 4 | 0 | - |
| scripts | 6 | 0 | ~4 KB |

**Total Project Files:** ~29 source files  
**Total Directories:** ~15 directories  
**Approximate Code Size:** ~89 KB

---

## 🚀 Quick Start Commands

```bash
# Start MCP Server
cd mosaic/mosaic-mcp
python src/server.py

# Start API Server
cd mosaic/mosaic-api/app
python api.py

# Start Frontend
cd mosaic/mosaic-ui
npm run dev
```

---

*This document is auto-generated and should be updated when the project structure changes.*
