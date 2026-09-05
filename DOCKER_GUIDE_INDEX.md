# 📚 MOSAIC Docker Documentation Guide

Complete guide to building, deploying, and managing MOSAIC with Docker.

## 📖 Documentation Structure

### Quick Start

- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - 5-minute quick start guide
  - Fastest way to get MOSAIC running
  - Essential commands and troubleshooting
  - Perfect for first-time users

### Build Guide

- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Comprehensive build instructions
  - Step-by-step image building
  - Individual vs bulk builds
  - Optimization and troubleshooting
  - Build time estimates and tips

### Complete Docker Guide

- **[DOCKER.md](DOCKER.md)** - Full Docker reference
  - Architecture and configuration
  - Development vs production
  - Volume management
  - GPU acceleration
  - Security and monitoring
  - Complete troubleshooting guide

### Configuration Files

- **[docker-compose.yml](docker-compose.yml)** - Production configuration
- **[docker-compose.dev.yml](docker-compose.dev.yml)** - Development with hot-reload
- **[docker-compose.gpu.yml](docker-compose.gpu.yml)** - GPU acceleration overlay
- **[.env.example](.env.example)** - Environment template

---

## 🎯 Choose Your Path

### I want to get started quickly

→ Start with **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)**

```bash
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

### I want to understand the build process

→ Read **[BUILD_GUIDE.md](BUILD_GUIDE.md)**

Learn about:

- Individual image builds
- Build optimization
- Troubleshooting build issues
- Tagging strategies

### I need complete Docker knowledge

→ Reference **[DOCKER.md](DOCKER.md)**

Covers:

- Architecture and networking
- Volume management and backups
- Security hardening
- GPU acceleration
- Production deployment
- Monitoring and logging

### I'm developing code

→ Use **[docker-compose.dev.yml](docker-compose.dev.yml)**

```bash
docker-compose -f docker-compose.dev.yml up
# Code changes auto-reload
```

---

## 🏗️ Docker Images Overview

MOSAIC consists of three Docker images:

### 1. mosaic-mcp (MCP Server)

**Purpose**: Video processing, frame extraction, embeddings, vector search

- **Image Size**: ~2.0-2.5 GB
- **Build Time**: 8-12 min (first), 1-2 min (cached)
- **Port**: 9090
- **Key Dependencies**:
  - Python 3.11
  - FFmpeg
  - PyTorch (CPU or GPU)
  - Transformers
  - ChromaDB, FAISS
  - Sentence Transformers

**Dockerfile**: [mosaic-mcp/Dockerfile](mosaic-mcp/Dockerfile)

### 2. mosaic-api (API Server)

**Purpose**: REST API, LangChain agent, MCP client

- **Image Size**: ~800 MB-1 GB
- **Build Time**: 4-6 min (first), 30-60 sec (cached)
- **Port**: 8000
- **Key Dependencies**:
  - Python 3.11
  - FastAPI + Uvicorn
  - LangChain ecosystem
  - MCP adapters
  - FFmpeg

**Dockerfile**: [mosaic-api/Dockerfile](mosaic-api/Dockerfile)

### 3. mosaic-ui (Frontend)

**Purpose**: Web interface, user interactions

- **Image Size**: ~200-300 MB
- **Build Time**: 3-5 min (first), 30-60 sec (cached)
- **Port**: 3000
- **Key Dependencies**:
  - Node.js 18 (Alpine)
  - Next.js 15
  - React 19
  - TailwindCSS

**Dockerfile**: [mosaic-ui/Dockerfile](mosaic-ui/Dockerfile)

### Total System

- **Combined Size**: ~3.0-3.8 GB
- **Total Build Time**: 15-23 min (first), 2-4 min (cached)
- **RAM Required**: 3-6 GB runtime, 8+ GB recommended
- **Disk Space**: 10-20 GB recommended

---

## 🐳 Docker Compose Files

### Production: docker-compose.yml

**Default production configuration**

```bash
docker-compose up -d
```

**Features**:

- Optimized builds
- Named volumes for persistence
- Health checks
- Auto-restart on failure
- Service dependencies

**Use for**: Production deployment, demos, stable testing

### Development: docker-compose.dev.yml

**Development with hot-reload**

```bash
docker-compose -f docker-compose.dev.yml up
```

**Features**:

- Source code mounted
- Debug logging
- Auto-reload on changes
- No build optimization

**Use for**: Active development, debugging

### GPU: docker-compose.gpu.yml

**GPU acceleration overlay**

```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**Features**:

- NVIDIA GPU support
- CUDA acceleration
- 10-50x faster processing

**Use for**: Heavy video processing, large models

**Requires**: NVIDIA GPU, CUDA drivers, nvidia-container-toolkit

---

## 📋 Common Workflows

### First Time Setup

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with API keys

# 2. Build images
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps
docker-compose logs -f
```

### Daily Development

```bash
# Start dev environment
make dev

# Make code changes → auto-reload

# Run tests
make test-api

# View logs
make logs-api

# Stop
make down
```

### Deploying Updates

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Verify
docker-compose ps
make logs
```

### Troubleshooting

```bash
# Check logs
docker-compose logs -f

# Check specific service
docker-compose logs mcp-server

# Restart service
docker-compose restart api-server

# Check health
curl http://localhost:8000/health

# Full reset
docker-compose down -v
docker system prune -af
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔧 Essential Commands Reference

### Docker Compose

```bash
docker-compose build              # Build all images
docker-compose up -d              # Start detached
docker-compose down               # Stop and remove
docker-compose down -v            # Stop and remove volumes
docker-compose logs -f            # Follow logs
docker-compose ps                 # List containers
docker-compose restart            # Restart all
docker-compose exec api-server bash  # Open shell
```

### Make Commands

```bash
make help          # Show all commands
make setup         # Initial setup
make build         # Build images
make up            # Start production
make dev           # Start development
make down          # Stop services
make logs          # View logs
make test          # Run tests
make clean         # Remove containers
make clean-all     # Remove everything
```

### Docker

```bash
docker images                     # List images
docker ps                         # List containers
docker logs <container>           # View logs
docker exec -it <container> bash  # Open shell
docker stats                      # Resource usage
docker system df                  # Disk usage
docker system prune -af           # Clean up
```

---

## 🔍 Verification Steps

### After Building

```bash
# 1. Check images exist
docker images | grep mosaic

# Expected output:
# mosaic-mcp    latest    ...    2.2 GB
# mosaic-api    latest    ...    950 MB
# mosaic-ui     latest    ...    245 MB

# 2. Verify total size
docker images --format "{{.Size}}" | head -3
```

### After Starting

```bash
# 1. Check services are running
docker-compose ps

# All should show "Up" and "(healthy)"

# 2. Test endpoints
curl http://localhost:9090/health  # MCP
curl http://localhost:8000/health  # API
curl http://localhost:3000         # UI (HTML)

# 3. Check logs for errors
docker-compose logs --tail=50
```

### Testing Functionality

```bash
# 1. Access frontend
# Open browser: http://localhost:3000

# 2. Upload a video
# Use the UI to upload a test video

# 3. Ask a question
# "What is in this video?"

# 4. Check logs
docker-compose logs -f api-server
```

---

## 📊 Resource Requirements

### Minimum Configuration

| Component | Minimum | Recommended       |
| --------- | ------- | ----------------- |
| RAM       | 8 GB    | 16 GB             |
| CPU       | 4 cores | 8+ cores          |
| Disk      | 10 GB   | 20 GB             |
| GPU       | None    | NVIDIA CUDA 11.8+ |

### Docker Desktop Settings

**Memory**: 8 GB minimum, 16 GB recommended
**CPU**: Allocate 4-8 cores
**Disk**: Ensure 20+ GB free space

**How to configure**:

- Windows/macOS: Docker Desktop → Settings → Resources
- Linux: Managed by system

---

## 🎓 Learning Path

### Beginner

1. Start with [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
2. Get services running with `docker-compose up -d`
3. Explore the frontend at http://localhost:3000
4. Review basic commands in [Common Workflows](#-common-workflows)

### Intermediate

1. Read [BUILD_GUIDE.md](BUILD_GUIDE.md) to understand builds
2. Try development mode with hot-reload
3. Learn volume management and backups
4. Experiment with different configurations

### Advanced

1. Study complete [DOCKER.md](DOCKER.md)
2. Configure GPU acceleration
3. Implement security hardening
4. Setup monitoring and logging
5. Deploy to production

---

## 🆘 Troubleshooting by Symptom

### "Services won't start"

→ See [DOCKER.md - Troubleshooting](DOCKER.md#-troubleshooting)

### "Build fails"

→ See [BUILD_GUIDE.md - Troubleshooting](BUILD_GUIDE.md#-troubleshooting-build-issues)

### "Out of memory"

→ Increase Docker memory in settings (8+ GB)

### "Port already in use"

→ Change port in docker-compose.yml

### "GPU not detected"

→ See [DOCKER.md - GPU Acceleration](DOCKER.md#-advanced-configuration)

---

## 📚 Additional Resources

### Internal Documentation

- [README.md](README.md) - Project overview
- [docs/architecture.md](docs/architecture.md) - System design
- [docs/deployment.md](docs/deployment.md) - Production deployment
- [docs/GPU_SETUP.md](docs/GPU_SETUP.md) - GPU configuration

### External Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

## 🎯 Quick Reference Card

```bash
# Setup (first time)
cp .env.example .env && make build && make up

# Start services
make up              # Production
make dev             # Development

# View logs
make logs            # All services
make logs-api        # API only
make logs-mcp        # MCP only

# Manage
make restart         # Restart all
make down            # Stop all
make clean           # Remove containers
make clean-all       # Full reset

# Test
make test            # All tests
make test-api        # API tests
make shell-api       # Open API shell

# Access
# Frontend:  http://localhost:3000
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

---

<div align="center">

**🎬 MOSAIC - Dockerized Video Analysis**

Complete documentation for building and running MOSAIC with Docker

[Quick Start](DOCKER_QUICKSTART.md) • [Build Guide](BUILD_GUIDE.md) • [Full Documentation](DOCKER.md)

</div>
