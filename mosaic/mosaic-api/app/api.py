from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import shutil
import uuid
from typing import Dict
from schemas import *
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
        
        # Initialize task status
        task_storage[task_id] = {
            "status": "processing",
            "video_id": video_id,
            "result": None
        }
        
        # Process video in background
        background_tasks.add_task(
            process_video_task,
            video_path,
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
        result = video_agent.chat(request.message, request.video_id)
        
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


@app.get("/clips/{clip_filename}")
async def get_clip(clip_filename: str):
    """Serve generated video clips."""
    clip_path = os.path.join("clips_output", clip_filename)
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    
    return FileResponse(clip_path, media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
