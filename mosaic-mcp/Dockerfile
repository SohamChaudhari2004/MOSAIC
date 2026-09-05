# =============================================================================
# Multi-stage build for mosaic-mcp (MCP Server) - Optimized for Size
# =============================================================================
# This Dockerfile uses multi-stage builds and optimizations to minimize image size
# Expected final size: ~2.5-3GB (down from 15GB)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies with build tools
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies (will be discarded in final stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .

# Step 1: Install PyTorch CPU-only (saves 2-3GB from CUDA libraries)
# Use extra-index-url to keep access to PyPI
RUN pip install --prefix=/install --no-cache-dir --no-warn-script-location \
    torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu

# Step 2: Install opencv-python-headless (instead of opencv-python, saves ~500MB)
RUN pip install --prefix=/install --no-cache-dir --no-warn-script-location \
    opencv-python-headless

# Step 3: Install remaining dependencies from requirements.txt
RUN pip install --prefix=/install --no-cache-dir --no-warn-script-location \
    groq \
    langchain \
    chromadb \
    faiss-cpu \
    transformers \
    sentence-transformers \
    Pillow \
    numpy \
    ffmpeg-python \
    python-dotenv \
    fastmcp \
    requests

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/usr/local/bin:$PATH

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # FFmpeg for video processing
    ffmpeg \
    # Required shared libraries for OpenCV and other packages
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libglib2.0-0 \
    libgl1 \
    # Clean up apt cache
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code (exclude tests in production)
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/storage/frames \
    /app/storage/chroma_db \
    /app/clips_output \
    /app/src/chroma_db

# Expose port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9090/health')" || exit 1

# Run the MCP server
CMD ["python", "src/server.py"]

# =============================================================================
# Build Instructions:
# =============================================================================
# Standard build:
#   docker build -t mosaic-mcp:latest .
#
# Build with BuildKit (faster):
#   DOCKER_BUILDKIT=1 docker build -t mosaic-mcp:latest .
#
# Check image size:
#   docker images mosaic-mcp:latest
#
# Expected size: ~2.5-3GB (compared to 15GB unoptimized)
# =============================================================================
