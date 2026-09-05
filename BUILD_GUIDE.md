# 🏗️ MOSAIC - Docker Image Build Guide

Complete step-by-step guide for building MOSAIC Docker images from scratch.

## 📋 Quick Reference

| Service        | Image Size   | Build Time | Dependencies                            |
| -------------- | ------------ | ---------- | --------------------------------------- |
| **mosaic-mcp** | ~2.0-2.5 GB  | 8-12 min   | FFmpeg, PyTorch, Transformers, ChromaDB |
| **mosaic-api** | ~800 MB-1 GB | 4-6 min    | FastAPI, LangChain, MCP adapters        |
| **mosaic-ui**  | ~200-300 MB  | 3-5 min    | Next.js, React, TailwindCSS             |
| **Total**      | ~3.0-3.8 GB  | 15-23 min  | -                                       |

---

## 🎯 Prerequisites

### Required Tools

```bash
# Check Docker installation
docker --version
# Required: Docker version 20.10+

# Check Docker Compose
docker-compose --version
# Required: Docker Compose version 2.0+

# Check available disk space
df -h .
# Required: 10-20 GB free space
```

### System Requirements

- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: 10 GB minimum (20 GB recommended)
- **CPU**: 4 cores minimum
- **Internet**: Stable connection for downloading base images and packages

---

## 🚀 Method 1: Build All Images (Recommended)

### Using Docker Compose

```bash
# Navigate to project root
cd mosaic

# Build all three images
docker-compose build

# Build with no cache (clean build)
docker-compose build --no-cache

# Build in parallel (faster on multi-core systems)
docker-compose build --parallel

# Build with verbose output
docker-compose build --progress=plain
```

### Using Make

```bash
# Simple one-command build
make build

# Build and start immediately
make build && make up

# Clean build from scratch
make clean && make build
```

### Expected Output

```
Building mcp-server
[+] Building 487.3s (14/14) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.2kB
 => [internal] load .dockerignore
 => [base 1/8] FROM docker.io/library/python:3.11-slim
 => [base 2/8] RUN apt-get update && apt-get install -y --no-install-recommends
 => [base 3/8] WORKDIR /app
 => [base 4/8] COPY requirements.txt pyproject.toml* ./
 => [base 5/8] RUN pip install --no-cache-dir -r requirements.txt
 => [base 6/8] COPY src/ ./src/
 ...
 => => naming to docker.io/library/mosaic_mcp-server

Building api-server
...

Building frontend
...

Successfully built mosaic-mcp, mosaic-api, mosaic-ui
```

---

## 🔨 Method 2: Build Individual Images

### 1. Build MCP Server

```bash
# Navigate to MCP directory
cd mosaic-mcp

# Basic build
docker build -t mosaic-mcp:latest .

# Build with specific tag
docker build -t mosaic-mcp:v1.0.0 .

# Build with multiple tags
docker build -t mosaic-mcp:latest -t mosaic-mcp:v1.0.0 .

# Clean build without cache
docker build --no-cache -t mosaic-mcp:latest .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t mosaic-mcp:latest .

# View detailed build progress
docker build --progress=plain -t mosaic-mcp:latest .
```

**What gets installed:**

- Base: Python 3.11 slim (~150 MB)
- FFmpeg and system libraries (~250 MB)
- PyTorch CPU version (~800-900 MB)
- Transformers library (~500 MB)
- ChromaDB, FAISS, Sentence Transformers (~500 MB)
- Other dependencies (~100 MB)

**Build time:** 8-12 minutes (first time), 1-2 minutes (cached)

### 2. Build API Server

```bash
# Navigate to API directory
cd mosaic-api

# Basic build
docker build -t mosaic-api:latest .

# With custom Python version
docker build --build-arg PYTHON_VERSION=3.11 -t mosaic-api:latest .

# Clean build
docker build --no-cache -t mosaic-api:latest .
```

**What gets installed:**

- Base: Python 3.11 slim (~150 MB)
- FFmpeg and libraries (~150 MB)
- FastAPI + Uvicorn (~50 MB)
- LangChain ecosystem (~300 MB)
- MCP adapters and clients (~100 MB)
- Other dependencies (~50 MB)

**Build time:** 4-6 minutes (first time), 30-60 seconds (cached)

### 3. Build Frontend

```bash
# Navigate to UI directory
cd mosaic-ui

# Basic build (multi-stage)
docker build -t mosaic-ui:latest .

# Build specific stage
docker build --target=deps -t mosaic-ui:deps .
docker build --target=builder -t mosaic-ui:builder .
docker build --target=runner -t mosaic-ui:latest .

# Clean build
docker build --no-cache -t mosaic-ui:latest .
```

**Build stages:**

1. **base**: Node.js 18 Alpine base image
2. **deps**: Install dependencies (package.json)
3. **builder**: Build Next.js application
4. **runner**: Production runtime (smallest)

**What gets installed:**

- Base: Node.js 18 Alpine (~180 MB)
- Dependencies (~100 MB in builder, removed in final image)
- Next.js standalone output (~50 MB)
- Static assets (~20 MB)

**Build time:** 3-5 minutes (first time), 30-60 seconds (cached)

---

## ⚡ Optimizing Build Speed

### 1. Enable BuildKit

BuildKit provides faster builds, better caching, and parallel execution.

**PowerShell (Windows):**

```powershell
$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build
```

**Bash (Linux/macOS):**

```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build
```

**Permanent (add to .env):**

```bash
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1
```

### 2. Use Layer Caching Effectively

**Good Dockerfile structure (cached efficiently):**

```dockerfile
# Dependencies change rarely → cached longer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Code changes frequently → invalidates cache less
COPY . .
```

**Bad structure (cache invalidated often):**

```dockerfile
# Code copied first → any change invalidates cache
COPY . .
# Dependencies re-installed every time
RUN pip install -r requirements.txt
```

### 3. Parallel Builds

```bash
# Build all images in parallel
docker-compose build --parallel

# Limit parallelism (if system has limited resources)
docker-compose build --parallel --max-concurrency=2
```

### 4. Use .dockerignore

Ensure `.dockerignore` files exist in each service directory to exclude unnecessary files:

```bash
# Check .dockerignore files exist
ls mosaic-api/.dockerignore
ls mosaic-mcp/.dockerignore
ls mosaic-ui/.dockerignore
```

### 5. Prune Docker System

Remove old images and caches to free up space:

```bash
# Remove unused images
docker image prune -a

# Remove build cache
docker builder prune

# Complete system cleanup
docker system prune -af

# Using make
make prune
```

---

## 🏷️ Tagging Strategy

### Development Tags

```bash
# Tag with 'dev' for development builds
docker build -t mosaic-api:dev .

# Tag with date
docker build -t mosaic-api:$(date +%Y%m%d) .

# Tag with git commit
docker build -t mosaic-api:$(git rev-parse --short HEAD) .
```

### Production Tags

```bash
# Tag with semantic version
docker build -t mosaic-api:1.0.0 -t mosaic-api:latest .

# Tag with version and latest
docker build -t mosaic-api:v1.0.0 -t mosaic-api:1.0 -t mosaic-api:latest .
```

### Viewing Tags

```bash
# List all MOSAIC images
docker images | grep mosaic

# Output:
# mosaic-mcp    latest    abc123    2.2 GB    2 hours ago
# mosaic-api    latest    def456    950 MB    2 hours ago
# mosaic-api    v1.0.0    def456    950 MB    2 hours ago
# mosaic-ui     latest    ghi789    245 MB    2 hours ago
```

---

## 🔍 Verifying Built Images

### Check Image Sizes

```bash
# List all MOSAIC images with sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep mosaic

# Check total size
docker images --format "{{.Size}}" | grep -v GB | awk '{sum+=$1} END {print sum " MB"}'
```

### Inspect Image Layers

```bash
# View image history and layers
docker history mosaic-mcp:latest

# Show layer sizes
docker history --human mosaic-mcp:latest --no-trunc
```

### Test Image

```bash
# Run temporary container to test
docker run --rm mosaic-mcp:latest python --version
docker run --rm mosaic-api:latest python -c "import fastapi; print(fastapi.__version__)"
docker run --rm mosaic-ui:latest node --version

# Check installed packages
docker run --rm mosaic-mcp:latest pip list
docker run --rm mosaic-api:latest pip list
docker run --rm mosaic-ui:latest npm list --depth=0
```

### Security Scan

```bash
# Scan for vulnerabilities (Docker Desktop)
docker scan mosaic-api:latest

# Or use Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image mosaic-api:latest
```

---

## 🐛 Troubleshooting Build Issues

### Build Fails: Network Timeout

**Symptom:** "Could not resolve hostname" or timeout errors

**Solution:**

```bash
# Configure DNS
# Docker Desktop → Settings → Docker Engine → Add:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

# Test network connectivity
docker run --rm alpine ping -c 3 google.com
```

### Build Fails: Out of Disk Space

**Symptom:** "no space left on device"

**Solution:**

```bash
# Check disk space
docker system df

# Clean up
docker system prune -af --volumes
docker builder prune -af

# Check again
docker system df
```

### Build Fails: Memory Issues

**Symptom:** "Killed" or OOM errors during build

**Solution:**

```bash
# Increase Docker memory
# Docker Desktop → Settings → Resources → Memory → 8+ GB

# Build with limited resources
docker-compose build --parallel --max-concurrency=1
```

### Build Fails: Base Image Pull Error

**Symptom:** "error pulling image"

**Solution:**

```bash
# Pull base images manually
docker pull python:3.11-slim
docker pull node:18-alpine

# Then rebuild
docker-compose build
```

### Build Fails: COPY Command Error

**Symptom:** "COPY failed: file not found"

**Solution:**

```bash
# Ensure you're in correct directory
pwd  # Should be mosaic/

# Check .dockerignore isn't excluding required files
cat mosaic-api/.dockerignore

# Check file exists
ls -la mosaic-api/requirements.txt
```

### Build is Extremely Slow

**Symptom:** Build takes >30 minutes

**Solution:**

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use parallel building
docker-compose build --parallel

# Check if Docker daemon is slow
docker info | grep -i "Operating System"

# On Windows/macOS: Ensure WSL2 backend is enabled
# Docker Desktop → Settings → General → Use WSL 2 based engine
```

---

## 📊 Build Time Optimization

### Expected Build Times

| Scenario              | MCP       | API       | UI        | Total     |
| --------------------- | --------- | --------- | --------- | --------- |
| **First build**       | 8-12 min  | 4-6 min   | 3-5 min   | 15-23 min |
| **Cached build**      | 1-2 min   | 30-60 sec | 30-60 sec | 2-4 min   |
| **Code only change**  | 10-30 sec | 10-20 sec | 20-40 sec | 40-90 sec |
| **Dependency change** | 5-8 min   | 2-4 min   | 2-3 min   | 9-15 min  |

### Tips for Faster Builds

1. **Keep dependencies stable**: Don't change `requirements.txt` or `package.json` unnecessarily
2. **Use BuildKit**: Always enable for faster builds
3. **Build in parallel**: Use `--parallel` flag
4. **Maintain cache**: Don't use `--no-cache` unless necessary
5. **Use SSD**: Build on SSD drive, not HDD
6. **Increase RAM**: Allocate more memory to Docker
7. **Use local registry**: Cache base images locally

---

## 📦 Pushing to Registry (Optional)

### Docker Hub

```bash
# Tag for Docker Hub
docker tag mosaic-api:latest yourusername/mosaic-api:latest

# Login
docker login

# Push
docker push yourusername/mosaic-api:latest
```

### Private Registry

```bash
# Tag for private registry
docker tag mosaic-api:latest registry.example.com/mosaic-api:latest

# Login to registry
docker login registry.example.com

# Push
docker push registry.example.com/mosaic-api:latest
```

### GitHub Container Registry

```bash
# Create GitHub personal access token with 'write:packages' scope

# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag
docker tag mosaic-api:latest ghcr.io/username/mosaic-api:latest

# Push
docker push ghcr.io/username/mosaic-api:latest
```

---

## ✅ Build Checklist

Before building:

- [ ] Docker and Docker Compose installed
- [ ] 10-20 GB disk space available
- [ ] 8+ GB RAM allocated to Docker
- [ ] Stable internet connection
- [ ] `.env` file created (optional for build)
- [ ] `.dockerignore` files present

Building:

- [ ] `docker-compose build` completes successfully
- [ ] All three images built (mcp-server, api-server, frontend)
- [ ] No error messages in build logs
- [ ] Image sizes reasonable (~3-4 GB total)

After building:

- [ ] Images listed in `docker images`
- [ ] Test images run without errors
- [ ] Ready to start with `docker-compose up -d`

---

## 🔗 Related Documentation

- [DOCKER.md](DOCKER.md) - Complete Docker usage guide
- [README.md](README.md) - Project overview and getting started
- [docs/architecture.md](docs/architecture.md) - System architecture
- [docs/deployment.md](docs/deployment.md) - Production deployment guide

---

## 🆘 Getting Help

**Build issues?**

1. Check [Troubleshooting](#-troubleshooting-build-issues) section above
2. Review Docker logs: `docker-compose build > build.log 2>&1`
3. Check [GitHub Issues](https://github.com/yourusername/mosaic/issues)
4. Ask in [Discussions](https://github.com/yourusername/mosaic/discussions)

**Include in bug reports:**

```bash
# System info
docker version
docker-compose version
uname -a  # or $PSVersionTable on Windows

# Docker disk usage
docker system df

# Build logs
docker-compose build > build.log 2>&1
```

---

<div align="center">

**🎬 MOSAIC - Building the Future of Video Analysis**

Happy Building! 🏗️

</div>
