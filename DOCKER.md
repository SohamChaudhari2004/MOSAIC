# 🐳 Docker Guide for MOSAIC

Complete guide for building, deploying, and managing MOSAIC with Docker.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building Docker Images](#building-docker-images)
  - [Individual Image Builds](#individual-image-builds)
  - [Building All Images](#building-all-images)
  - [Image Size Reference](#image-size-reference)
- [Docker Compose Setup](#docker-compose-setup)
  - [Production Configuration](#production-configuration)
  - [Development Configuration](#development-configuration)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Volume Management](#volume-management)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## 📖 Overview

MOSAIC uses a **microservices architecture** with three Docker containers:

| Service        | Purpose                                     | Port | Base Image       | Est. Size    |
| -------------- | ------------------------------------------- | ---- | ---------------- | ------------ |
| **mosaic-mcp** | Video processing, embeddings, vector search | 9090 | python:3.11-slim | ~2.0-2.5 GB  |
| **mosaic-api** | FastAPI backend, LangChain agent            | 8000 | python:3.11-slim | ~800 MB-1 GB |
| **mosaic-ui**  | Next.js frontend                            | 3000 | node:18-alpine   | ~200-300 MB  |

**Total Size**: ~3.0-3.8 GB (with GPU support: ~5-6 GB)

---

## 📦 Prerequisites

### Required Software

- **Docker**: Version 20.10+ ([Download](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (included with Docker Desktop)
- **Git**: For cloning the repository

### System Requirements

| Component      | Minimum    | Recommended                |
| -------------- | ---------- | -------------------------- |
| **RAM**        | 8 GB       | 16 GB                      |
| **Disk Space** | 10 GB free | 20 GB free                 |
| **CPU**        | 4 cores    | 8+ cores                   |
| **GPU**        | Optional   | NVIDIA GPU with CUDA 11.8+ |

### API Keys (Required)

You'll need API keys from these providers:

1. **Mistral AI**: [Sign up](https://console.mistral.ai/) - for LLM agent
2. **Groq**: [Sign up](https://console.groq.com/) - for fast inference

---

## 🚀 Quick Start

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd mosaic

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment

Edit `.env` and add your API keys:

```bash
# Required API Keys
MISTRAL_API_KEY=your_mistral_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Build and Run

**Option A: Using Docker Compose (Recommended)**

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**Option B: Using Make Commands**

```bash
# Windows PowerShell or Unix terminal
make setup    # Setup environment
make build    # Build all images
make up       # Start services
make logs     # View logs
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MCP Health**: http://localhost:9090/health

---

## 🏗️ Building Docker Images

### Understanding the Build Process

Each service has its own `Dockerfile` that defines:

1. Base image selection
2. System dependencies installation
3. Python/Node.js package installation
4. Application code copying
5. Runtime configuration

### Individual Image Builds

#### 1. Building mosaic-mcp (MCP Server)

```bash
# Navigate to MCP directory
cd mosaic-mcp

# Build the image
docker build -t mosaic-mcp:latest .

# With custom tags
docker build -t mosaic-mcp:v1.0 -t mosaic-mcp:latest .

# Without cache (clean build)
docker build --no-cache -t mosaic-mcp:latest .

# View build progress
docker build --progress=plain -t mosaic-mcp:latest .
```

**What's installed:**

- Python 3.11 + system libraries
- FFmpeg for video processing
- PyTorch (CPU version) ~800 MB
- Transformers library ~500 MB
- ChromaDB, FAISS, Sentence Transformers
- Video processing libraries (OpenCV, Pillow)

#### 2. Building mosaic-api (API Server)

```bash
# Navigate to API directory
cd mosaic-api

# Build the image
docker build -t mosaic-api:latest .

# With build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t mosaic-api:latest .
```

**What's installed:**

- Python 3.11 + system libraries
- FastAPI + Uvicorn
- LangChain ecosystem (langchain, langchain-groq, langchain-mistralai)
- MCP adapters for tool integration
- HTTP clients (httpx, requests)

#### 3. Building mosaic-ui (Frontend)

```bash
# Navigate to UI directory
cd mosaic-ui

# Build the image
docker build -t mosaic-ui:latest .

# Multi-stage build shows each stage
docker build --progress=plain -t mosaic-ui:latest .
```

**What's included:**

- Node.js 18 Alpine base ~180 MB
- Next.js 15 optimized production build
- React 19 + TailwindCSS
- Standalone output (minimal size)

### Building All Images

#### Using Docker Compose (Recommended)

```bash
# Build all images from root directory
docker-compose build

# Build with no cache (clean build)
docker-compose build --no-cache

# Build specific service
docker-compose build mcp-server
docker-compose build api-server
docker-compose build frontend

# Build in parallel (faster)
docker-compose build --parallel

# Build with progress output
docker-compose build --progress plain
```

#### Using Make Commands

```bash
# Build all images
make build

# Build and start immediately
make build && make up

# Clean build from scratch
make clean && make build
```

#### Build Time Estimates

| Service    | First Build   | Cached Build | Clean Build   |
| ---------- | ------------- | ------------ | ------------- |
| mosaic-mcp | 8-12 min      | 1-2 min      | 10-15 min     |
| mosaic-api | 4-6 min       | 30-60 sec    | 5-8 min       |
| mosaic-ui  | 3-5 min       | 30-60 sec    | 4-6 min       |
| **Total**  | **15-23 min** | **2-4 min**  | **19-29 min** |

_Times vary based on internet speed and CPU_

### Image Size Reference

```bash
# List all built images
docker images | grep mosaic

# Expected output:
# mosaic-mcp    latest    abc123    2.2 GB
# mosaic-api    latest    def456    950 MB
# mosaic-ui     latest    ghi789    245 MB
```

### Optimizing Build Performance

**1. Use Build Cache**

Docker caches layers. Order your Dockerfile from least to most frequently changed:

```dockerfile
# ✅ Good - dependencies cached
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# ❌ Bad - invalidates cache often
COPY . .
RUN pip install -r requirements.txt
```

**2. Multi-Stage Builds**

The UI already uses this (see `mosaic-ui/Dockerfile`):

```dockerfile
FROM node:18-alpine AS base
FROM base AS deps          # Install dependencies
FROM base AS builder       # Build application
FROM base AS runner        # Production runtime
```

**3. Use .dockerignore**

Create `.dockerignore` in each service directory:

```gitignore
# mosaic-api/.dockerignore
__pycache__
*.pyc
.env
.git
tests/
*.md
node_modules
```

**4. Build with BuildKit**

```bash
# Enable BuildKit (faster builds)
$env:DOCKER_BUILDKIT=1  # PowerShell
export DOCKER_BUILDKIT=1  # Bash

docker-compose build
```

---

## � Docker Compose Setup

### Understanding the Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Network (mosaic-network)     │
│  ┌──────────────────────────────────────┐  │
│  │  Frontend (mosaic-ui)                │  │
│  │  Port: 3000                          │  │
│  │  ↓ Connects to                       │  │
│  └──────────────────────────────────────┘  │
│               ↓                             │
│  ┌──────────────────────────────────────┐  │
│  │  API Server (mosaic-api)             │  │
│  │  Port: 8000                          │  │
│  │  ↓ Connects to                       │  │
│  └──────────────────────────────────────┘  │
│               ↓                             │
│  ┌──────────────────────────────────────┐  │
│  │  MCP Server (mosaic-mcp)             │  │
│  │  Port: 9090                          │  │
│  │  • Video Processing                  │  │
│  │  • Vector Search (FAISS + ChromaDB)  │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘

Volumes:
├── storage_data → Shared video uploads & frames
├── chroma_data  → Vector database persistence
└── clips_data   → Generated video clips
```

### Production Configuration

The `docker-compose.yml` file defines the production setup:

```yaml
version: "3.8"

services:
  # MCP Server - Video processing backend
  mcp-server:
    build:
      context: ./mosaic-mcp
      dockerfile: Dockerfile
    container_name: mosaic-mcp
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - storage_data:/app/storage # Shared storage
      - chroma_data:/app/src/chroma_db # Vector DB
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    networks:
      - mosaic-network
    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import requests; requests.get('http://localhost:9090/health')",
        ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s # Allow 60s for model loading

  # API Server - FastAPI backend
  api-server:
    build:
      context: ./mosaic-api
      dockerfile: Dockerfile
    container_name: mosaic-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    depends_on:
      mcp-server:
        condition: service_healthy # Wait for MCP to be ready
    volumes:
      - storage_data:/app/storage
      - clips_data:/app/clips_output
    environment:
      - MCP_SERVER_URL=http://mcp-server:9090 # Internal DNS
      - DATABASE_URL=sqlite:///./storage/mosaic.db
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    networks:
      - mosaic-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Frontend - Next.js UI
  frontend:
    build:
      context: ./mosaic-ui
      dockerfile: Dockerfile
    container_name: mosaic-ui
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      api-server:
        condition: service_healthy # Wait for API to be ready
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000 # Browser-side
      - NEXT_TELEMETRY_DISABLED=1
      - NODE_ENV=production
    env_file:
      - .env
    networks:
      - mosaic-network

# Shared network for inter-container communication
networks:
  mosaic-network:
    driver: bridge

# Persistent volumes
volumes:
  storage_data:
    driver: local
  chroma_data:
    driver: local
  clips_data:
    driver: local
```

### Development Configuration

Create `docker-compose.dev.yml` for development with hot-reload:

```yaml
version: "3.8"

services:
  mcp-server:
    build:
      context: ./mosaic-mcp
      target: base
    volumes:
      - ./mosaic-mcp/src:/app/src:rw # Hot reload
      - storage_data:/app/storage
      - chroma_data:/app/src/chroma_db
    environment:
      - LOG_LEVEL=DEBUG
      - PYTHONUNBUFFERED=1
    env_file:
      - .env

  api-server:
    build:
      context: ./mosaic-api
      target: base
    volumes:
      - ./mosaic-api/app:/app/app:rw # Hot reload
      - storage_data:/app/storage
    environment:
      - LOG_LEVEL=DEBUG
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    command: uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./mosaic-ui
      target: deps
    volumes:
      - ./mosaic-ui:/app:rw # Hot reload
      - /app/node_modules # Use container's node_modules
      - /app/.next # Use container's build cache
    environment:
      - NODE_ENV=development
    command: npm run dev

volumes:
  storage_data:
  chroma_data:

networks:
  mosaic-network:
    driver: bridge
```

---

## ⚙️ Environment Configuration

### Setting Up .env File

1. **Copy the template:**

```bash
cp .env.example .env
```

2. **Edit `.env` with your API keys:**

```bash
# Required API Keys
MISTRAL_API_KEY=sk-your-actual-mistral-key-here
GROQ_API_KEY=gsk_your-actual-groq-key-here

# Optional: SERP API for web search
SERP_API_KEY=your-serp-api-key-here

# Optional: Gemini for vision tasks
GEMINI_API_KEY=your-gemini-api-key-here
```

### Key Environment Variables

#### Server Configuration

```bash
# MCP Server (internal Docker communication)
MCP_SERVER_URL=http://mcp-server:9090  # Use container name
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=9090

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (browser-side URL)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Use localhost for browser
```

#### Storage Paths

```bash
# All paths are relative to container's /app directory
STORAGE_BASE_DIR=storage
UPLOAD_DIR=storage/uploads
STORAGE_DIR=storage/frames
CLIPS_OUTPUT_DIR=storage/clips
CHROMA_DB_DIR=storage/chroma_db
```

#### AI Model Configuration

```bash
# Device: auto (detect GPU), cuda (force GPU), cpu (force CPU)
DEVICE=auto

# Embedding models
EMBEDDING_MODEL=clip-ViT-B-32
TEXT_EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM configuration
LLM_MODEL=mistral-large-latest
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
```

#### Performance Tuning

```bash
# Frame extraction rate (frames per second)
FRAME_RATE=1

# Batch size for processing
BATCH_SIZE=32

# Maximum file size (bytes)
MAX_FILE_SIZE=1000000000  # 1GB

# Request timeout (seconds)
REQUEST_TIMEOUT=300

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

### Validating Configuration

```bash
# Check if variables are loaded
docker-compose config

# Verify specific service config
docker-compose config | grep MISTRAL_API_KEY

# Test connectivity
docker-compose run --rm api-server env | grep API_KEY
```

---

## 🚀 Running the Application

### Production Deployment

#### Method 1: Docker Compose Commands

```bash
# Step 1: Build images (first time or after code changes)
docker-compose build

# Step 2: Start services in detached mode
docker-compose up -d

# Step 3: Check service health
docker-compose ps

# Expected output:
# NAME         STATUS              PORTS
# mosaic-mcp   Up (healthy)        0.0.0.0:9090->9090/tcp
# mosaic-api   Up (healthy)        0.0.0.0:8000->8000/tcp
# mosaic-ui    Up                  0.0.0.0:3000->3000/tcp

# Step 4: Watch logs
docker-compose logs -f

# Stop watching: Ctrl+C
```

#### Method 2: Make Commands

```bash
# Setup (first time only)
make setup

# Build all images
make build

# Start services
make up

# View logs
make logs

# Stop services
make down
```

#### Method 3: Start with Logs (Foreground)

```bash
# Start and watch logs (Ctrl+C to stop)
docker-compose up

# Or with make
make up-logs
```

### Development Mode

Development mode enables hot-reload for faster iteration:

```bash
# Start with hot-reload
docker-compose -f docker-compose.dev.yml up

# Or detached
docker-compose -f docker-compose.dev.yml up -d

# Using make
make dev      # Foreground
make dev-d    # Background
```

**What's different in dev mode:**

- Source code mounted as volumes → changes reflect immediately
- Debug logging enabled
- No build optimization
- Auto-reload on file changes

### Verifying the Deployment

#### 1. Check Service Status

```bash
# All services
docker-compose ps

# Health checks
docker-compose exec mcp-server curl http://localhost:9090/health
docker-compose exec api-server curl http://localhost:8000/health
```

#### 2. Test Endpoints

**MCP Server:**

```bash
curl http://localhost:9090/health
# Expected: {"status": "healthy", "service": "mcp-server"}
```

**API Server:**

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "api-server"}

# Test API docs
curl http://localhost:8000/docs
```

**Frontend:**

```bash
curl http://localhost:3000
# Expected: HTML response
```

#### 3. Check Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs mcp-server
docker-compose logs api-server
docker-compose logs frontend

# Follow logs (live)
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50

# Since specific time
docker-compose logs --since=10m
```

### Managing Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api-server

# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop frontend

# Start stopped services
docker-compose start

# Remove stopped containers
docker-compose down

# Remove and delete volumes (DATA LOSS!)
docker-compose down -v
```

### Updating Images

```bash
# Rebuild specific service
docker-compose build --no-cache mcp-server
docker-compose up -d mcp-server

# Rebuild all services
docker-compose build --no-cache
docker-compose up -d

# Pull latest code and rebuild
git pull
docker-compose build
docker-compose up -d
```

### Accessing Running Containers

```bash
# Open shell in API container
docker-compose exec api-server /bin/bash

# Open shell in MCP container
docker-compose exec mcp-server /bin/bash

# Open shell in UI container (Alpine uses /bin/sh)
docker-compose exec frontend /bin/sh

# Run one-off command
docker-compose exec api-server python -c "print('Hello')"

# Using make
make shell-api
make shell-mcp
make shell-ui
```

### Running Tests

```bash
# Run all tests
docker-compose run --rm api-server pytest tests/ -v
docker-compose run --rm mcp-server pytest tests/ -v

# Using make
make test       # All tests
make test-api   # API tests only
make test-mcp   # MCP tests only

# Run specific test file
docker-compose run --rm api-server pytest tests/test_api/test_chat.py -v

# With coverage
docker-compose run --rm api-server pytest --cov=app tests/
```

---

## 💾 Volume Management

### Understanding Volumes

Docker volumes persist data across container restarts. MOSAIC uses three named volumes:

| Volume         | Purpose                                   | Typical Size   | Shared Between         |
| -------------- | ----------------------------------------- | -------------- | ---------------------- |
| `storage_data` | Video uploads, extracted frames, database | 1-100 GB       | mcp-server, api-server |
| `chroma_data`  | Vector embeddings database                | 100 MB - 10 GB | mcp-server only        |
| `clips_data`   | Generated video clips                     | 1-50 GB        | api-server only        |

### Managing Volumes

#### List All Volumes

```bash
# List all Docker volumes
docker volume ls

# Filter MOSAIC volumes
docker volume ls | grep mosaic

# Expected output:
# local     mosaic_storage_data
# local     mosaic_chroma_data
# local     mosaic_clips_data
```

#### Inspect Volume Details

```bash
# View volume configuration
docker volume inspect mosaic_storage_data

# Output shows mount point on host
# "Mountpoint": "/var/lib/docker/volumes/mosaic_storage_data/_data"
```

#### Backup Volumes

**PowerShell (Windows):**

```powershell
# Create backup directory
New-Item -ItemType Directory -Force -Path ./backups

# Backup storage data
docker run --rm `
  -v mosaic_storage_data:/data:ro `
  -v ${PWD}/backups:/backup `
  alpine tar czf /backup/storage_$(Get-Date -Format 'yyyyMMdd').tar.gz /data

# Backup chroma data
docker run --rm `
  -v mosaic_chroma_data:/data:ro `
  -v ${PWD}/backups:/backup `
  alpine tar czf /backup/chroma_$(Get-Date -Format 'yyyyMMdd').tar.gz /data
```

**Bash (Linux/macOS):**

```bash
# Create backup directory
mkdir -p ./backups

# Backup storage data
docker run --rm \
  -v mosaic_storage_data:/data:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/storage_$(date +%Y%m%d).tar.gz /data

# Backup chroma data
docker run --rm \
  -v mosaic_chroma_data:/data:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chroma_$(date +%Y%m%d).tar.gz /data
```

#### Restore Volumes

**PowerShell:**

```powershell
# Restore storage data
docker run --rm `
  -v mosaic_storage_data:/data `
  -v ${PWD}/backups:/backup `
  alpine sh -c "cd / && tar xzf /backup/storage_20260215.tar.gz"
```

**Bash:**

```bash
# Restore storage data
docker run --rm \
  -v mosaic_storage_data:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "cd / && tar xzf /backup/storage_20260215.tar.gz"
```

#### Copy Files to/from Volumes

```bash
# Copy file FROM volume to host
docker run --rm -v mosaic_storage_data:/data alpine \
  cat /data/path/to/file.mp4 > ./output.mp4

# Copy file TO volume from host
docker run --rm -i -v mosaic_storage_data:/data alpine \
  sh -c "cat > /data/path/to/file.mp4" < ./input.mp4

# Or use running container
docker cp ./video.mp4 mosaic-mcp:/app/storage/uploads/
docker cp mosaic-api:/app/storage/mosaic.db ./backup.db
```

#### Clean Up Volumes

```bash
# Remove specific volume (DATA LOSS!)
docker volume rm mosaic_storage_data

# Remove all MOSAIC volumes (DATA LOSS!)
docker volume rm mosaic_storage_data mosaic_chroma_data mosaic_clips_data

# Remove volumes when stopping services
docker-compose down -v

# Remove unused volumes
docker volume prune

# Using make (includes confirmation)
make clean-all
```

#### Check Volume Size

```bash
# Get volume size
docker system df -v

# Or inspect specific volume
docker run --rm -v mosaic_storage_data:/data alpine du -sh /data
```

### Development Mode - Bind Mounts

In development mode, source code is mounted directly:

```yaml
# docker-compose.dev.yml
services:
  api-server:
    volumes:
      - ./mosaic-api/app:/app/app:rw # Read-write mount
      - storage_data:/app/storage # Named volume

  mcp-server:
    volumes:
      - ./mosaic-mcp/src:/app/src:rw
      - storage_data:/app/storage
      - chroma_data:/app/src/chroma_db

  frontend:
    volumes:
      - ./mosaic-ui:/app:rw
      - /app/node_modules # Exclude node_modules
      - /app/.next # Exclude .next
```

**Benefits:**

- Changes reflect immediately (hot-reload)
- No rebuild needed
- Easier debugging

**Caveats:**

- Slower on Windows/macOS (file system overhead)
- Must exclude `node_modules` and build directories

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Services Won't Start

**Symptom:** `docker-compose up` fails or services exit immediately

**Diagnosis:**

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs

# Check specific service
docker-compose logs mcp-server
```

**Common Causes:**

**a) Missing API Keys**

```bash
# Verify .env file exists
ls .env

# Check if loaded
docker-compose config | grep API_KEY

# Solution: Add API keys to .env
MISTRAL_API_KEY=your-key-here
GROQ_API_KEY=your-key-here
```

**b) Port Already in Use**

```powershell
# Windows - Check what's using port 8000
netstat -ano | findstr :8000
# Find process ID (PID) and kill it or change port

# Solution: Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 on host
```

```bash
# Linux/macOS - Check port usage
lsof -i :8000
sudo kill -9 <PID>
```

**c) Insufficient Memory**

```bash
# Check Docker memory allocation
docker info | grep Memory

# Solution: Increase Docker Desktop memory
# Settings → Resources → Memory → Set to 8+ GB
```

#### 2. Build Failures

**Symptom:** `docker-compose build` fails

**Diagnosis:**

```bash
# Build with verbose output
docker-compose build --progress=plain

# Build without cache
docker-compose build --no-cache
```

**Common Causes:**

**a) Network Issues**

```bash
# Test network connectivity
docker run --rm alpine ping -c 3 google.com

# Solution: Check firewall/proxy settings
# Or use different DNS
# Docker Desktop → Settings → Docker Engine → Add:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

**b) Disk Space**

```bash
# Check available space
docker system df

# Clean up
docker system prune -af
docker volume prune

# Using make
make prune
```

**c) Invalid Dockerfile**

```bash
# Verify Dockerfile syntax
docker build -t test ./mosaic-mcp

# Check for Windows line endings (should be LF, not CRLF)
# In VS Code: Check bottom right → "CRLF" → Change to "LF"
```

#### 3. Container Health Check Failures

**Symptom:** Service shows as "unhealthy"

**Diagnosis:**

```bash
# Check health status
docker-compose ps

# Inspect health check
docker inspect mosaic-mcp | grep -A 10 Health

# View health check logs
docker logs mosaic-mcp
```

**Solutions:**

**a) Service Not Ready**

```yaml
# Increase start_period in docker-compose.yml
healthcheck:
  start_period: 120s # Give more time for model loading
```

**b) Health Check Command Fails**

```bash
# Test health check manually
docker-compose exec mcp-server curl http://localhost:9090/health

# Or if curl not available
docker-compose exec mcp-server python -c "import requests; print(requests.get('http://localhost:9090/health').json())"
```

#### 4. API Connection Errors

**Symptom:** Frontend can't connect to API

**Diagnosis:**

```bash
# Test API from host
curl http://localhost:8000/health

# Test from within container
docker-compose exec frontend curl http://api-server:8000/health
```

**Solutions:**

**a) Wrong API URL**

```bash
# In .env, ensure:
NEXT_PUBLIC_API_URL=http://localhost:8000  # For browser
# NOT: http://api-server:8000 (internal only)
```

**b) Network Issues**

```bash
# Verify all containers on same network
docker network inspect mosaic_mosaic-network

# Restart networking
docker-compose down
docker network prune
docker-compose up -d
```

#### 5. Volume Permission Issues (Linux)

**Symptom:** "Permission denied" errors

**Solution:**

```bash
# Fix ownership
sudo chown -R $USER:$USER storage/

# Or run with specific user
docker-compose run --user $(id -u):$(id -g) api-server bash

# Add to docker-compose.yml
services:
  api-server:
    user: "${UID}:${GID}"
```

#### 6. Out of Memory Errors

**Symptom:** Container exits with code 137 (OOM killed)

**Diagnosis:**

```bash
# Monitor memory usage
docker stats

# Check logs for OOM
docker-compose logs mcp-server | grep -i "memory\|oom"
```

**Solutions:**

**a) Increase Docker Memory**

```bash
# Docker Desktop → Resources → Memory → 16 GB
```

**b) Add Resource Limits**

```yaml
# docker-compose.yml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          memory: 6G
        reservations:
          memory: 2G
```

**c) Optimize Application**

```bash
# In .env - Reduce batch size
BATCH_SIZE=16  # Instead of 32

# Use CPU instead of loading large models
DEVICE=cpu
```

#### 7. Video Processing Failures

**Symptom:** Video upload fails or processing errors

**Diagnosis:**

```bash
# Check FFmpeg is installed
docker-compose exec mcp-server ffmpeg -version

# Test video file
docker-compose exec mcp-server ffprobe /app/storage/uploads/video.mp4

# Check storage space
docker-compose exec mcp-server df -h
```

**Solutions:**

**a) Install FFmpeg**

```dockerfile
# Ensure in Dockerfile
RUN apt-get update && apt-get install -y ffmpeg
```

**b) Check File Format**

```bash
# Convert to supported format
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

**c) Increase Upload Size**

```python
# In mosaic-api/app/api.py
app.add_middleware(
    ...,
    max_upload_size=2000000000  # 2GB
)
```

#### 8. ChromaDB/FAISS Errors

**Symptom:** Vector search fails

**Diagnosis:**

```bash
# Check ChromaDB directory
docker-compose exec mcp-server ls -la /app/src/chroma_db

# View logs
docker-compose logs mcp-server | grep -i chroma
```

**Solutions:**

**a) Reset Vector Database**

```bash
# Stop services
docker-compose down

# Remove chroma volume
docker volume rm mosaic_chroma_data

# Restart
docker-compose up -d
```

**b) Check Disk Space**

```bash
docker-compose exec mcp-server df -h /app/src/chroma_db
```

### Quick Diagnostic Commands

```bash
# Full system check
docker --version
docker-compose --version
docker ps -a
docker images
docker volume ls
docker network ls
docker system df

# Service health check
for service in mcp-server api-server frontend; do
  echo "=== $service ==="
  docker-compose exec $service echo "OK" 2>/dev/null || echo "FAILED"
done

# Export all logs for debugging
docker-compose logs > mosaic-debug.log 2>&1

# Clean slate (nuclear option)
docker-compose down -v
docker system prune -af --volumes
rm -rf storage/
make setup
make build
make up
```

### Getting Help

If you're still stuck:

1. **Export logs:**

   ```bash
   docker-compose logs > logs.txt
   ```

2. **Check configuration:**

   ```bash
   docker-compose config > config.yml
   ```

3. **System info:**

   ```bash
   docker info > docker-info.txt
   docker version >> docker-info.txt
   ```

4. **Create GitHub issue** with:
   - Error message
   - Relevant logs
   - Docker version
   - OS information
   - Steps to reproduce

---

## ⚙️ Advanced Configuration

### Resource Limits

Control CPU and memory usage per service:

```yaml
# docker-compose.yml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: "2.0" # Max 2 CPU cores
          memory: 4G # Max 4GB RAM
        reservations:
          cpus: "1.0" # Guarantee 1 core
          memory: 2G # Guarantee 2GB RAM

  api-server:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 2G
        reservations:
          cpus: "0.5"
          memory: 1G

  frontend:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
```

### Custom Networks

Configure network settings:

```yaml
networks:
  mosaic-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
    driver_opts:
      com.docker.network.bridge.name: mosaic_br
```

### Environment-Specific Overrides

Use multiple compose files:

```bash
# Base configuration
# docker-compose.yml

# Production overrides
# docker-compose.prod.yml
services:
  mcp-server:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

# Development overrides
# docker-compose.dev.yml
services:
  mcp-server:
    volumes:
      - ./mosaic-mcp/src:/app/src:rw

# Usage:
# docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Custom Build Arguments

Pass build-time variables:

```yaml
# docker-compose.yml
services:
  api-server:
    build:
      context: ./mosaic-api
      args:
        PYTHON_VERSION: 3.11
        BUILD_DATE: ${BUILD_DATE:-unknown}
        GIT_COMMIT: ${GIT_COMMIT:-unknown}
```

```dockerfile
# mosaic-api/Dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ARG BUILD_DATE
ARG GIT_COMMIT
LABEL build_date="${BUILD_DATE}"
LABEL git_commit="${GIT_COMMIT}"
```

```bash
# Build with custom args
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export GIT_COMMIT=$(git rev-parse HEAD)
docker-compose build
```

### Health Check Customization

Advanced health check configuration:

```yaml
services:
  mcp-server:
    healthcheck:
      test: |
        python -c "
        import requests
        import sys
        try:
            r = requests.get('http://localhost:9090/health', timeout=5)
            sys.exit(0 if r.status_code == 200 else 1)
        except:
            sys.exit(1)
        "
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 90s
```

### Logging Configuration

Configure logging drivers:

```yaml
services:
  mcp-server:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
        labels: "service,environment"
        tag: "{{.ImageName}}/{{.Name}}/{{.ID}}"

  # Or use syslog
  api-server:
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://192.168.0.42:123"
        tag: "mosaic-api"
```

### Security Hardening

#### Run as Non-Root User

```dockerfile
# mosaic-api/Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 mosaic && \
    mkdir -p /app/storage && \
    chown -R mosaic:mosaic /app

USER mosaic

WORKDIR /app
# ... rest of Dockerfile
```

```yaml
# docker-compose.yml
services:
api-server:
  user: "1000:1000"
  read_only: true
  tmpfs:
    - /tmp
    - /app/.cache
```

#### Limit Capabilities

```yaml
services:
  api-server:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    security_opt:
      - no-new-privileges:true
```

#### Use Secrets for API Keys

```yaml
# For Docker Swarm or using external secrets
services:
  api-server:
    secrets:
      - mistral_api_key
      - groq_api_key
    environment:
      MISTRAL_API_KEY_FILE: /run/secrets/mistral_api_key

secrets:
  mistral_api_key:
    file: ./secrets/mistral_api_key.txt
  groq_api_key:
    file: ./secrets/groq_api_key.txt
```

### GPU Acceleration

Enable NVIDIA GPU support for 10-50x faster processing:

#### Prerequisites

1. **NVIDIA GPU** with CUDA support
2. **NVIDIA drivers** installed on host
3. **NVIDIA Container Toolkit**

**Install NVIDIA Container Toolkit (Linux):**

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Windows (WSL2) / macOS:**

```bash
# GPU support available in Docker Desktop with WSL2 backend
# Enable in: Docker Desktop → Settings → Resources → WSL Integration
```

#### Enable GPU in Docker Compose

**Option 1: Use GPU compose file**

```bash
# Start with GPU support
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**Option 2: Modify docker-compose.yml**

```yaml
services:
  mcp-server:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1 # or 'all' for all GPUs
              capabilities: [gpu]
```

#### GPU-Optimized Dockerfile

```dockerfile
# mosaic-mcp/Dockerfile.gpu
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch with CUDA support
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install FAISS GPU version
RUN pip install faiss-gpu

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Rest of Dockerfile...
```

#### Configure for GPU

```bash
# In .env
DEVICE=cuda  # Force GPU
# or
DEVICE=auto  # Auto-detect (recommended)
```

#### Verify GPU Usage

```bash
# Check GPU is accessible
docker-compose exec mcp-server nvidia-smi

# Check PyTorch sees GPU
docker-compose exec mcp-server python -c "
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')
"

# Monitor GPU usage during processing
watch -n 1 nvidia-smi
```

### Multi-Stage Build Optimization

Optimize image size with multi-stage builds:

```dockerfile
# Stage 1: Builder
FROM python:3.11 AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY app/ ./app/

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Optimization

#### Enable BuildKit

```bash
# PowerShell
$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1

# Bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Or set in .env
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1
```

#### Optimize Layer Caching

```dockerfile
# ✅ Good: Install deps before copying code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# ❌ Bad: Code changes invalidate dep cache
COPY . .
RUN pip install -r requirements.txt
```

#### Use .dockerignore

```bash
# mosaic-api/.dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist/
build/
.env
.git/
.vscode/
.idea/
tests/
*.md
.pytest_cache/
htmlcov/
.coverage
```

### Monitoring and Observability

#### Prometheus Metrics

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

#### Export Metrics from Application

```python
# Add to mosaic-api/app/api.py
from prometheus_client import Counter, Histogram, make_asgi_app

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 📚 Common Workflows

### Daily Development Workflow

```bash
# 1. Start development environment
make dev-d

# 2. Make code changes (auto-reloads)
# Edit files in mosaic-api/app/ or mosaic-mcp/src/

# 3. View logs if needed
make logs-api

# 4. Run tests
make test-api

# 5. Stop when done
make down
```

### Deploying Updates

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild images
docker-compose build

# 3. Restart services with zero downtime
docker-compose up -d

# 4. Verify deployment
docker-compose ps
curl http://localhost:8000/health
make logs
```

### Database Backup Routine

```bash
# PowerShell script for automated backups
# backup.ps1
$date = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "./backups/$date"
New-Item -ItemType Directory -Force -Path $backupDir

# Backup database
docker cp mosaic-api:/app/storage/mosaic.db "$backupDir/mosaic.db"

# Backup volumes
docker run --rm `
  -v mosaic_storage_data:/data:ro `
  -v ${PWD}/$backupDir:/backup `
  alpine tar czf /backup/storage.tar.gz /data

# Keep only last 7 backups
Get-ChildItem ./backups | Sort-Object CreationTime -Descending | Select-Object -Skip 7 | Remove-Item -Recurse
```

### Scaling for Production

```bash
# 1. Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 2. Add reverse proxy (Nginx)
docker run -d \
  --name nginx \
  --network mosaic_mosaic-network \
  -p 80:80 \
  -p 443:443 \
  -v ./nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

# 3. Enable monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# 4. Setup SSL with Let's Encrypt
docker run --rm \
  -v ./certbot:/etc/letsencrypt \
  -v ./certbot-var:/var/lib/letsencrypt \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d yourdomain.com
```

### Testing New Features

```bash
# 1. Create test branch
git checkout -b feature/new-feature

# 2. Start clean environment
make clean
make setup
make build

# 3. Test feature
make dev
# Manually test feature

# 4. Run automated tests
make test

# 5. Clean up
make down
git checkout main
```

### Debugging Production Issues

```bash
# 1. Export all logs
docker-compose logs --since=1h > debug-$(date +%Y%m%d-%H%M%S).log

# 2. Check resource usage
docker stats --no-stream

# 3. Inspect specific service
docker-compose exec api-server /bin/bash
# Inside container:
# - Check disk: df -h
# - Check memory: free -h
# - Check processes: ps aux
# - Test connections: curl http://mcp-server:9090/health

# 4. Restart troubled service
docker-compose restart api-server

# 5. Check if issue persists
docker-compose logs -f api-server
```

---

## 📝 Best Practices

### Development

1. **Use .dockerignore files**
   - Exclude unnecessary files from build context
   - Speeds up builds significantly

2. **Keep images small**
   - Use Alpine/slim base images
   - Multi-stage builds for production
   - Clear package manager caches

3. **Layer caching**
   - Order Dockerfile commands from least to most frequently changed
   - Install dependencies before copying source code

4. **Environment variables**
   - Never commit sensitive keys
   - Use `.env` for local, secrets for production
   - Validate required variables on startup

5. **Health checks**
   - Implement health endpoints in all services
   - Set appropriate timeouts and start periods
   - Use health checks for dependency ordering

### Production

1. **Resource limits**
   - Set memory and CPU limits
   - Prevent one service from starving others
   - Monitor resource usage

2. **Logging**
   - Use JSON logging for structured logs
   - Limit log file sizes
   - Centralize logs (ELK, Splunk, etc.)

3. **Security**
   - Run containers as non-root
   - Use read-only filesystems where possible
   - Scan images for vulnerabilities
   - Keep base images updated

4. **Backups**
   - Automate volume backups
   - Test restore procedures
   - Store backups off-host

5. **Monitoring**
   - Set up health monitoring
   - Track key metrics (CPU, memory, response times)
   - Configure alerts for failures

6. **Updates**
   - Test updates in staging first
   - Use rolling updates for zero downtime
   - Keep rollback plan ready

### Images

1. **Tagging strategy**

   ```bash
   # Tag with version and latest
   docker build -t mosaic-api:1.2.3 -t mosaic-api:latest .

   # Use Git commit SHA for traceability
   docker build -t mosaic-api:$(git rev-parse --short HEAD) .
   ```

2. **Registry best practices**

   ```bash
   # Push to registry
   docker tag mosaic-api:latest registry.example.com/mosaic-api:latest
   docker push registry.example.com/mosaic-api:latest

   # Pull from registry
   docker pull registry.example.com/mosaic-api:latest
   ```

3. **Image scanning**

   ```bash
   # Scan for vulnerabilities
   docker scan mosaic-api:latest

   # Or use Trivy
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     aquasec/trivy image mosaic-api:latest
   ```

---

## 🔍 Command Reference

### Docker Compose Commands

```bash
# Build
docker-compose build                    # Build all services
docker-compose build --no-cache         # Build without cache
docker-compose build api-server         # Build specific service
docker-compose build --parallel         # Build in parallel

# Start/Stop
docker-compose up                       # Start (foreground)
docker-compose up -d                    # Start (background)
docker-compose up --build               # Build and start
docker-compose down                     # Stop and remove containers
docker-compose down -v                  # Stop and remove volumes
docker-compose stop                     # Stop containers
docker-compose start                    # Start stopped containers
docker-compose restart                  # Restart containers

# View
docker-compose ps                       # List containers
docker-compose logs                     # View logs
docker-compose logs -f                  # Follow logs
docker-compose logs --tail=100          # Last 100 lines
docker-compose logs api-server          # Specific service logs
docker-compose top                      # Display running processes

# Execute
docker-compose exec api-server bash     # Open shell
docker-compose exec -T api-server cmd   # Run command
docker-compose run --rm api-server test # One-off command

# Config
docker-compose config                   # Validate and view config
docker-compose config --services        # List services
docker-compose config --volumes         # List volumes

# Scale
docker-compose up -d --scale mcp-server=2  # Scale service

# Pull/Push
docker-compose pull                     # Pull latest images
docker-compose push                     # Push images to registry
```

### Make Commands

```bash
make help          # Show available commands
make setup         # Initial setup (.env)
make build         # Build all images
make up            # Start production
make dev           # Start development
make dev-d         # Start development (detached)
make down          # Stop services
make restart       # Restart services
make logs          # View logs
make logs-api      # API logs
make logs-mcp      # MCP logs
make logs-ui       # UI logs
make ps            # Show containers
make clean         # Remove containers/images
make clean-all     # Remove everything + data
make prune         # Clean Docker system
make test          # Run all tests
make test-api      # Run API tests
make test-mcp      # Run MCP tests
make shell-api     # Shell in API container
make shell-mcp     # Shell in MCP container
make shell-ui      # Shell in UI container
```

### Docker Commands

```bash
# Images
docker images                           # List images
docker rmi <image-id>                   # Remove image
docker image prune                      # Remove unused images
docker build -t name:tag .              # Build image

# Containers
docker ps                               # List running containers
docker ps -a                            # List all containers
docker rm <container-id>                # Remove container
docker container prune                  # Remove stopped containers
docker logs <container-id>              # View logs
docker exec -it <container-id> bash     # Open shell
docker stats                            # Resource usage

# Volumes
docker volume ls                        # List volumes
docker volume inspect <volume-name>     # Inspect volume
docker volume rm <volume-name>          # Remove volume
docker volume prune                     # Remove unused volumes

# Networks
docker network ls                       # List networks
docker network inspect <network-name>   # Inspect network
docker network prune                    # Remove unused networks

# System
docker system df                        # Disk usage
docker system prune                     # Remove unused data
docker system prune -a --volumes        # Remove everything unused
docker info                             # System information
docker version                          # Docker version
```

---

## 🎯 Common Tasks

### Reset Everything

```bash
# Complete reset (nuclear option)
make clean-all
# Or manually:
docker-compose down -v
docker system prune -af --volumes
rm -rf storage/
cp .env.example .env
# Edit .env with your keys
docker-compose build
docker-compose up -d
```

### Update Single Service

```bash
# Rebuild and restart API only
docker-compose build api-server
docker-compose up -d --no-deps api-server
```

### View Real-time Logs

```bash
# All services
docker-compose logs -f --tail=50

# Specific service with timestamps
docker-compose logs -f -t api-server

# Multiple services
docker-compose logs -f api-server mcp-server
```

### Database Operations

```bash
# Backup database
docker cp mosaic-api:/app/storage/mosaic.db ./backup.db

# Restore database
docker cp ./backup.db mosaic-api:/app/storage/mosaic.db
docker-compose restart api-server

# Access SQLite database
docker-compose exec api-server sqlite3 /app/storage/mosaic.db
# .tables - list tables
# .schema <table> - show schema
# .quit - exit
```

### Performance Monitoring

```bash
# Real-time stats
docker stats

# Specific containers
docker stats mosaic-api mosaic-mcp mosaic-ui

# Export stats
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Documentation**: https://docs.docker.com/compose/
- **Dockerfile Best Practices**: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- **Docker Security**: https://docs.docker.com/engine/security/
- **MOSAIC GPU Setup**: [docs/GPU_SETUP.md](docs/GPU_SETUP.md)
- **MOSAIC Architecture**: [docs/architecture.md](docs/architecture.md)
- **API Reference**: [docs/api-reference.md](docs/api-reference.md)

---

## 🆘 Support

**Having issues?**

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Review [GitHub Issues](https://github.com/yourusername/mosaic/issues)
3. Join [Discussions](https://github.com/yourusername/mosaic/discussions)
4. Check [FAQ](docs/FAQ.md)

**Reporting bugs:**

```bash
# Collect diagnostic info
docker-compose config > config.txt
docker-compose logs > logs.txt
docker version > version.txt
docker system df > disk.txt

# Create issue with:
# - Description of problem
# - Steps to reproduce
# - Expected vs actual behavior
# - Attach diagnostic files
```

---

<div align="center">

**🎬 MOSAIC - Multimodal Open-Source AI for Intelligent Content**

Making video analysis accessible through containerization! 🚀

[Documentation](docs/) • [API Reference](docs/api-reference.md) • [Contributing](CONTRIBUTING.md) • [License](LICENSE)

</div>
