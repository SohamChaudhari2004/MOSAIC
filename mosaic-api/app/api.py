from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import sys
import shutil
import uuid
import asyncio
import logging
from typing import Dict, Optional
from schemas import *
# Use new MCP-based agent with fallback to original
try:
    from agent_mcp import VideoAgent
except ImportError:
    from agent import VideoAgent
from mcp_client import MCPClient
from config import *

from schemas import VideoUploadResponse, ChatRequest, ChatResponse, TaskStatusResponse

app = FastAPI(title="Mosaic Video API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
video_agent = VideoAgent()
mcp_client = MCPClient(MCP_SERVER_URL)

# Storage for background tasks
task_storage: Dict[str, Dict] = {}

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Directory for temporary media uploads (images/audio for search)
MEDIA_UPLOAD_DIR = os.path.join(APP_DIR, "storage", "media_uploads")
os.makedirs(MEDIA_UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Mosaic Video API", "status": "running"}


@app.post("/upload-video", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process a video file."""
    try:
        # Generate unique IDs
        video_id = str(uuid.uuid4())[:8]
        task_id = str(uuid.uuid4())
        
        # Save uploaded file
        video_path = os.path.join(UPLOAD_DIR, f"{video_id}_{file.filename}")
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Register the video path with the agent for clip generation
        video_agent.register_video(video_id, os.path.abspath(video_path))
        
        # Initialize task status
        task_storage[task_id] = {
            "status": "processing",
            "video_id": video_id,
            "video_path": os.path.abspath(video_path),
            "result": None
        }
        
        # Process video in background
        background_tasks.add_task(
            process_video_task,
            os.path.abspath(video_path),
            video_id,
            task_id
        )
        
        return VideoUploadResponse(
            status="accepted",
            video_id=video_id,
            task_id=task_id,
            message="Video uploaded successfully. Processing in background."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_video_task(video_path: str, video_id: str, task_id: str):
    """Background task to process video."""
    try:
        result = mcp_client.process_video(video_path, video_id)
        task_storage[task_id] = {
            "status": "completed",
            "video_id": video_id,
            "result": result
        }
    except Exception as e:
        task_storage[task_id] = {
            "status": "failed",
            "video_id": video_id,
            "error": str(e)
        }


@app.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get status of video processing task."""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error")
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with video agent."""
    try:
        # Build message with media context if provided
        message = request.message
        if request.media_path and request.media_type:
            if request.media_type == "image":
                message = f"[User uploaded an image for visual search: {request.media_path}] {message or 'Find visually similar scenes in the video and generate a clip of the best match.'}"
            elif request.media_type == "audio":
                message = f"[User uploaded an audio clip for audio search: {request.media_path}] {message or 'Find matching audio segments in the video and generate a clip of the best match.'}"
        
        result = video_agent.chat(message, request.video_id)
        
        return ChatResponse(
            response=result["response"],
            video_id=request.video_id,
            metadata={"success": result["success"]}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset-memory")
async def reset_memory():
    """Clear agent conversation history."""
    video_agent.reset_memory()
    return {"message": "Memory cleared successfully"}


@app.post("/clear-storage")
async def clear_storage():
    """Clear all storage directories including uploaded videos, frames, clips, and databases."""
    try:
        # Try to clear MCP server storage (may fail if MCP server is down)
        mcp_result = {"status": "skipped", "message": "MCP server not available"}
        try:
            mcp_result = mcp_client.clear_storage()
        except Exception as mcp_error:
            mcp_result = {"status": "error", "error": str(mcp_error)}
        
        # Clear API uploads directory
        api_stats = {"files_deleted": 0, "errors": []}
        for dir_to_clear in [UPLOAD_DIR, MEDIA_UPLOAD_DIR]:
            if os.path.exists(dir_to_clear):
                for item in os.listdir(dir_to_clear):
                    item_path = os.path.join(dir_to_clear, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                        api_stats["files_deleted"] += 1
                    except Exception as e:
                        api_stats["errors"].append(str(e))
        
        # Clear task storage
        task_storage.clear()
        
        # Reset agent memory
        video_agent.reset_memory()
        
        return {
            "status": "success",
            "message": "All storage cleared successfully",
            "mcp_storage": mcp_result,
            "api_storage": api_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos")
async def list_videos():
    """List all processed videos."""
    try:
        result = mcp_client.list_videos()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos/{video_id}")
async def get_video_info(video_id: str):
    """Get information about a specific video."""
    try:
        result = mcp_client.get_video_info(video_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/clips/{video_id}/{clip_filename}")
async def get_clip(video_id: str, clip_filename: str):
    """Serve generated video clips."""
    clip_path = os.path.join("clips_output", video_id, clip_filename)
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    
    return FileResponse(clip_path, media_type="video/mp4")


@app.post("/upload-media")
async def upload_media(
    file: UploadFile = File(...),
):
    """
    Upload an image or audio file for search. Returns the saved file path.
    The actual search happens through the /chat endpoint via the agent.
    """
    try:
        filename = file.filename or "upload"
        ext = os.path.splitext(filename)[1].lower()
        
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        audio_extensions = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".wma"}
        
        if ext not in image_extensions and ext not in audio_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Supported: images, audio"
            )
        
        # Save uploaded file
        file_id = str(uuid.uuid4())[:8]
        saved_path = os.path.join(MEDIA_UPLOAD_DIR, f"{file_id}_{filename}")
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_path = os.path.abspath(saved_path)
        media_type = "image" if ext in image_extensions else "audio"
        
        return {
            "status": "success",
            "media_path": saved_path,
            "media_type": media_type,
            "filename": filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/media/{filename}")
async def serve_media(filename: str):
    """Serve uploaded media files (images/audio)."""
    media_path = os.path.join(MEDIA_UPLOAD_DIR, filename)
    if not os.path.exists(media_path):
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(media_path)


if __name__ == "__main__":
    # Fix for Windows asyncio connection reset errors during video streaming
    if sys.platform == "win32":
        # Use SelectorEventLoop instead of ProactorEventLoop on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Suppress ConnectionResetError logging
        class ConnectionResetFilter(logging.Filter):
            def filter(self, record):
                return "ConnectionResetError" not in str(record.msg) and \
                       "WinError 10054" not in str(record.msg)
        
        logging.getLogger("asyncio").addFilter(ConnectionResetFilter())
    
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
