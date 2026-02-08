from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class VideoUploadResponse(BaseModel):
    status: str
    video_id: str
    task_id: str
    message: str

class ChatRequest(BaseModel):
    message: str
    video_id: Optional[str] = None
    session_id: Optional[str] = None
    media_path: Optional[str] = None
    media_type: Optional[str] = None  # "image" or "audio"

class ChatResponse(BaseModel):
    response: str
    video_id: Optional[str] = None
    clips: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
