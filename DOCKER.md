# 🐳 Docker Guide for MOSAIC

This guide covers everything you need to know about running MOSAIC with Docker.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Docker Images](#docker-images)
- [Docker Compose](#docker-compose)
- [Development vs Production](#development-vs-production)
- [Volume Management](#volume-management)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your API keys
# Required: MISTRAL_API_KEY, GROQ_API_KEY

# 3. Start all services
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Using Make (Windows/Unix)

```bash
# Setup environment
make setup

# Start production mode
make up

# Start development mode
make dev

# View logs
make logs
```

---

## 📦 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB minimum for images and volumes
- **API Keys**:
  - [Mistral AI](https://console.mistral.ai/)
  - [Groq](https://console.groq.com/)

### Installing Docker

#### Windows

```powershell
# Using winget
winget install Docker.DockerDesktop

# Or download from: https://www.docker.com/products/docker-desktop
```

#### macOS

```bash
# Using Homebrew
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

---

## 🖼️ Docker Images

MOSAIC consists of three Docker images:

### 1. mosaic-mcp (MCP Server)

- **Base**: `python:3.11-slim`
- **Size**: ~2.5GB (with models)
- **Purpose**: Video processing, embedding generation, search
- **Port**: 9090

**Features**:

- FFmpeg for video processing
- FAISS for vector search
- ChromaDB for text embeddings
- Sentence Transformers models

### 2. mosaic-api (FastAPI Backend)

- **Base**: `python:3.11-slim`
- **Size**: ~1.5GB
- **Purpose**: REST API, LangChain agent orchestration
- **Port**: 8000

**Features**:

- FastAPI for REST endpoints
- LangChain ReAct agent
- MCP client for tool calls
- Health checks

### 3. mosaic-ui (Next.js Frontend)

- **Base**: `node:18-alpine`
- **Size**: ~200MB
- **Purpose**: Web interface
- **Port**: 3000

**Features**:

- Next.js 15 with React 19
- TypeScript
- TailwindCSS
- Optimized production build

---

## 🎼 Docker Compose

### Services Architecture

```yaml
mosaic-network (bridge)
│
├── mcp-server (9090)
│   ├── Volumes: storage_data, chroma_data
│   └── Health check: HTTP GET /health
│
├── api-server (8000)
│   ├── Depends on: mcp-server
│   ├── Volumes: storage_data, clips_data
│   └── Health check: HTTP GET /health
│
└── frontend (3000)
    ├── Depends on: api-server
    └── Env: NEXT_PUBLIC_API_URL
```

### Production Configuration (`docker-compose.yml`)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart api-server
```

**Features**:

- Named volumes for persistence
- Health checks for reliability
- Automatic restart on failure
- Network isolation

### Development Configuration (`docker-compose.dev.yml`)

```bash
# Start development mode
docker-compose -f docker-compose.dev.yml up

# Or use make
make dev
```

**Features**:

- Source code mounted as volumes (hot reload)
- Debug logging enabled
- Development dependencies included
- No build optimization

---

## 🔄 Development vs Production

### Production Mode

```bash
docker-compose up -d
```

**Characteristics**:

- Optimized builds
- Named volumes (persistence)
- Minimal logging (INFO level)
- Health checks enabled
- Automatic restarts
- No source code mounting

**Use cases**:

- Deployment
- Demo environments
- Testing with real data

### Development Mode

```bash
docker-compose -f docker-compose.dev.yml up
```

**Characteristics**:

- Source code hot-reload
- Debug logging (DEBUG level)
- Development dependencies
- Bind mounts for code
- No image optimization

**Use cases**:

- Active development
- Testing changes quickly
- Debugging issues

---

## 💾 Volume Management

### Named Volumes (Production)

```bash
# List volumes
docker volume ls | grep mosaic

# Inspect a volume
docker volume inspect mosaic_storage_data

# Backup volumes
docker run --rm -v mosaic_storage_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/storage_backup.tar.gz /data

# Restore volumes
docker run --rm -v mosaic_storage_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/storage_backup.tar.gz -C /
```

### Volumes Used:

- **storage_data**: Video uploads, frames, metadata
- **chroma_data**: ChromaDB vector database
- **clips_data**: Generated video clips

### Bind Mounts (Development)

```yaml
volumes:
  - ./mosaic-api/app:/app/app # API source code
  - ./mosaic-mcp/src:/app/src # MCP source code
  - ./mosaic-ui:/app # UI source code
```

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs mcp-server

# Check health status
docker-compose ps
```

### Out of Memory

```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory → 8GB+

# Check resource usage
docker stats
```

### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Map host 8001 to container 8000
```

### Build Failures

```bash
# Clean build cache
docker-compose build --no-cache

# Remove all containers and images
docker-compose down --rmi all

# Prune Docker system
docker system prune -af
```

### Volume Permission Issues (Linux)

```bash
# Fix permissions
sudo chown -R $(id -u):$(id -g) storage/

# Run as specific user
docker-compose run --user $(id -u):$(id -g) api-server bash
```

### API Keys Not Working

```bash
# Check if .env is loaded
docker-compose config

# Verify environment variables in container
docker-compose exec api-server env | grep API_KEY
```

---

## ⚙️ Advanced Configuration

### Custom Network

```yaml
networks:
  mosaic-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Resource Limits

```yaml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 4G
        reservations:
          cpus: "1"
          memory: 2G
```

### Custom Dockerfile

```bash
# Build with custom Dockerfile
docker-compose build --build-arg PYTHON_VERSION=3.12
```

### Multi-Stage Build Optimization

```dockerfile
# Use build cache efficiently
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### Health Check Customization

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 🎯 Common Tasks

### Rebuild Specific Service

```bash
docker-compose build --no-cache api-server
docker-compose up -d api-server
```

### Scale Services

```bash
# Not recommended for this architecture
docker-compose up -d --scale mcp-server=2
```

### View Resource Usage

```bash
docker stats
```

### Clean Up Everything

```bash
# Stop and remove containers, volumes, images
docker-compose down -v --rmi all

# Clean Docker system
docker system prune -af --volumes

# Or use make
make clean-all
```

### Export Logs

```bash
docker-compose logs > mosaic-logs.txt
docker-compose logs --since 1h > recent-logs.txt
```

### Database Reset

```bash
# Remove database volume
docker volume rm mosaic_storage_data

# Or use manual cleanup
rm -rf storage/mosaic.db
```

---

## 🚀 GPU Acceleration with Docker

Enable NVIDIA GPU acceleration for 10-50x faster video processing.

### Prerequisites

1. **NVIDIA GPU** with CUDA support
2. **NVIDIA drivers** installed on host
3. **NVIDIA Container Toolkit**:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**Verify installation:**

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Enable GPU in Docker Compose

**Option 1: Use GPU compose override (Recommended)**

```bash
# Start with GPU support
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# Check GPU is detected
docker exec mosaic-mcp python -c "import torch; print('GPU:', torch.cuda.is_available())"
```

**Option 2: Uncomment GPU config in docker-compose.yml**

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

### GPU Configuration

Set in `.env`:

```bash
# Use CUDA GPU
DEVICE=cuda

# Or auto-detect (recommended)
DEVICE=auto

# Force CPU (for testing)
DEVICE=cpu
```

### Docker Image with GPU

Update `mosaic-mcp/Dockerfile` to use CUDA base image:

```dockerfile
# Use CUDA-enabled base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y python3.11 python3-pip

# Install PyTorch with CUDA
RUN pip install torch --index-url https://download.pytorch.org/whl/cu118

# Install FAISS GPU (optional)
RUN pip install faiss-gpu

# Continue with normal setup...
```

### Verify GPU Usage

```bash
# Check GPU is available in container
docker exec mosaic-mcp nvidia-smi

# Check PyTorch sees GPU
docker exec mosaic-mcp python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

# Monitor GPU usage during processing
watch -n 1 nvidia-smi
```

### Troubleshooting GPU in Docker

**Issue: "could not select device driver"**

```bash
# Restart Docker daemon
sudo systemctl restart docker

# Check NVIDIA runtime is configured
docker info | grep -i runtime
```

**Issue: GPU not detected in container**

```bash
# Verify host can see GPU
nvidia-smi

# Check container has GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Issue: CUDA version mismatch**

```bash
# Check host CUDA version
nvidia-smi

# Use matching CUDA base image in Dockerfile
FROM nvidia/cuda:XX.X.X-cudnn8-runtime-ubuntu22.04
```

> 📖 **Full GPU Guide**: See [docs/GPU_SETUP.md](docs/GPU_SETUP.md) for detailed GPU configuration

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Check system resources: `docker stats`
4. Review [GitHub Issues](https://github.com/yourusername/mosaic/issues)
5. Join our [Discussions](https://github.com/yourusername/mosaic/discussions)

---

<div align="center">

**MOSAIC Docker Setup** - Making deployment seamless! 🚀

</div>
