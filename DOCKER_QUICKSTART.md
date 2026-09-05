# 🚀 MOSAIC Docker Quick Start

Get MOSAIC running in 5 minutes with Docker!

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 8+ GB RAM, 10+ GB disk space
- API keys: [Mistral AI](https://console.mistral.ai/), [Groq](https://console.groq.com/)

## Quick Start

```bash
# 1. Clone and navigate
cd mosaic

# 2. Setup environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Build and run
docker-compose build
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Using Make Commands

```bash
make setup    # Setup .env file
make build    # Build all images
make up       # Start services
make logs     # View logs
make down     # Stop services
```

## Image Sizes

| Service    | Size            | Purpose                          |
| ---------- | --------------- | -------------------------------- |
| mosaic-mcp | ~2.0-2.5 GB     | Video processing, vector search  |
| mosaic-api | ~800 MB-1 GB    | FastAPI backend, LangChain agent |
| mosaic-ui  | ~200-300 MB     | Next.js frontend                 |
| **Total**  | **~3.0-3.8 GB** |                                  |

## Common Commands

```bash
# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart api-server

# Access shell
docker-compose exec api-server /bin/bash

# Run tests
docker-compose run --rm api-server pytest

# Clean everything
docker-compose down -v
```

## Development Mode

Hot-reload enabled for development:

```bash
docker-compose -f docker-compose.dev.yml up
```

## GPU Acceleration

For 10-50x faster processing with NVIDIA GPU:

```bash
# Requires: nvidia-container-toolkit
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

## Troubleshooting

**Services won't start?**

```bash
docker-compose logs
docker-compose ps
```

**Port already in use?**

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"
```

**Out of memory?**

```bash
# Docker Desktop → Settings → Resources → Memory → 8+ GB
```

**Build failures?**

```bash
docker-compose build --no-cache
docker system prune -af
```

## Documentation

- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Detailed build instructions
- **[DOCKER.md](DOCKER.md)** - Complete Docker guide
- **[README.md](README.md)** - Project overview
- **[docs/](docs/)** - Additional documentation

## Architecture

```
Frontend (3000) → API Server (8000) → MCP Server (9090)
                                          ↓
                     Video Processing + Vector Search
```

## Volumes

- `storage_data` - Video uploads & frames (shared)
- `chroma_data` - Vector database
- `clips_data` - Generated clips

## Health Checks

```bash
curl http://localhost:9090/health  # MCP Server
curl http://localhost:8000/health  # API Server
curl http://localhost:3000         # Frontend
```

## Stopping Services

```bash
# Stop (keeps data)
docker-compose down

# Stop and remove data (WARNING!)
docker-compose down -v
```

## Next Steps

1. Upload a video via the frontend (http://localhost:3000)
2. Ask questions about the video in the chat
3. View processed frames and generated clips
4. Check [docs/user-guide.md](docs/user-guide.md) for features

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mosaic/issues)
- **Docs**: [Full Documentation](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mosaic/discussions)

---

<div align="center">

**Made with ❤️ by the MOSAIC Team**

[Documentation](docs/) • [API Reference](docs/api-reference.md) • [Contributing](CONTRIBUTING.md)

</div>
