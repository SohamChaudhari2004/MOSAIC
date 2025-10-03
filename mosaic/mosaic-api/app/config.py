import os
from dotenv import load_dotenv

load_dotenv()

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:9090")

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

# Storage Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
STORAGE_DIR = os.getenv("STORAGE_DIR", "mosaic/extracted_frames")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
