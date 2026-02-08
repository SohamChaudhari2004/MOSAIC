"""
File to expose all the tools via mcp server(using fastmcp)
Tool1 : video_processor
Tool2 : search_text
Tool3 : search_image
Tool4 : search_speech
Tool5 : summarize_video
Tool6 : get_video_info
Tool7 : list_videos
"""

from mcp.server.fastmcp import FastMCP
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional
from fastapi import Request
from starlette.responses import JSONResponse
from video_processor import VideoProcessingPipeline
from search_engine import MultimodalSearchEngine , get_video_clips_from_hits

load_dotenv()

mcp = FastMCP(
    name="mosaic-mcp-server",
    instructions="This is the Mosaic MCP server for video analysis and processing. Use proper tools for different tasks as per the instructions.",
)

storage_dir = os.path.abspath(os.getenv("STORAGE_DIR", "storage/frames"))
video_processor = VideoProcessingPipeline(storage_dir=storage_dir)
search_engine = MultimodalSearchEngine(storage_dir=storage_dir)




# ============== TOOL 1: Video Processor ==============
@mcp.tool(
    name="process_video",
    description="Process a video to extract frames, transcripts, captions, and audio. and store the embeddings for search.",
    
)
def process_video(video_path: str, video_id: str) -> Dict:
    """
    Process and index a video file.
    Extracts keyframes, generates captions, transcribes audio,
    and stores embeddings in vector databases (FAISS + ChromaDB).
    
    Args:
        video_path: Path to the video file to process
        video_id: Unique identifier for this video
        
    Returns:
        Dictionary with processing status, statistics, and transcript.
    """

    try:
        result = video_processor.process_video(
            video_path = video_path,
            video_id = video_id,
            )
        
        return result

    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "video_id": video_id
        }
    

# ============== TOOL 2: Search Text/Transcript ==============
@mcp.tool(
    name="search_text",
    description="Search for text in the video transcript's  and return relevant clips.",

)
def search_text(query: str, video_id: str, k: int = 2) -> List[Dict]:
    """
    Search video transcript using text query.
    Returns matching transcript segments with timestamps.
    
    Args:
        query: Text query to search for in transcripts
        video_id: ID of the video to search
        k: Number of results to return (default: 5)
        
    Returns:
        List of matching transcript segments with start/end times and distances
    """
    try:
        results = search_engine.search_text(
            query = query,
            video_id= video_id,
            k = k
        )
        return results
    except Exception as e:
        return [{
            "error": str(e),
            "query": query,
            "video_id": video_id
        }]


# ============== TOOL 3: Search by Image/Frame ==============
@mcp.tool(
    name="search_image",
    description="Search for similar frames in the video using an image query and return relevant clips.",
    
)
def search_image(
    query_image_path: str, 
    video_id: str, 
    k: int = 2, 
    fps: float = 30.0
    ) -> List[Dict]:
    """
    Search video frames using image similarity (CLIP embeddings).
    Returns similar frames with clip timing parameters.
    
    Args:
        query_image_path: Path to query image file
        video_id: ID of the video to search
        k: Number of results to return (default: 5)
        fps: Frames per second for timestamp calculation (default: 30.0)
        
    Returns:
        List of similar frames with paths, distances, timestamps, and clip parameters
    """
    try:
        results = search_engine.search_image(
            query_image_path = query_image_path,
            video_id= video_id,
            k = k,
            fps = fps
        )
        return results
    except Exception as e:
        return [{
            "error": str(e),
            "query_image_path": query_image_path,
            "video_id": video_id
        }]
    
# ===== Tool 4: Search by Caption =====
@mcp.tool(
    name="search_caption",
    description="Search for relevant frames using AI-generated captions. Good for finding specific objects, actions, or scenes described in text.",
)
def search_caption(
    query: str, 
    video_id: str, 
    k: int = 5, 
    fps: float = 30.0
) -> List[Dict]:
    """
    Search video frame captions using text query.
    Captions are AI-generated descriptions of each frame.
    Returns matching frames with clip timing parameters.
    
    Args:
        query: Text query to search in frame captions (e.g., "person talking on phone")
        video_id: ID of the video to search
        k: Number of results to return (default: 5)
        fps: Frames per second for timestamp calculation (default: 30.0)
        
    Returns:
        List of matching frames with captions, paths, timestamps, and clip parameters
    """
    try:
        results = search_engine.search_caption(
            query=query,
            video_id=video_id,
            k=k,
            fps=fps
        )
        return results
    except Exception as e:
        return [{
            "error": str(e),
            "query": query,
            "video_id": video_id
        }]


# ===== Tool 4b: Visual Search using CLIP =====
@mcp.tool(
    name="search_visual",
    description="Search for frames using CLIP visual-semantic search. Best for finding visual content that matches a text description. More accurate than caption search for visual similarity.",
)
def search_visual(
    query: str, 
    video_id: str, 
    k: int = 5, 
    fps: float = 30.0
) -> List[Dict]:
    """
    Search video frames using CLIP visual-semantic embeddings.
    This uses the same CLIP model to encode text and find visually similar frames.
    More powerful than caption-based search for visual content.
    
    Args:
        query: Text description of visual content to find (e.g., "red car", "sunset over mountains")
        video_id: ID of the video to search
        k: Number of results to return (default: 5)
        fps: Frames per second for timestamp calculation (default: 30.0)
        
    Returns:
        List of matching frames with paths, distances, timestamps, and clip parameters
    """
    try:
        results = search_engine.search_visual(
            query_text=query,
            video_id=video_id,
            k=k,
            fps=fps
        )
        return results
    except Exception as e:
        return [{
            "error": str(e),
            "query": query,
            "video_id": video_id
        }]


# ============== TOOL 5: Generate Video Clips ==============
# ===== Tool 5: Generate Video Clips =====
@mcp.tool(
    name="generate_clips",
    description="Generate video clips from search results based on timing information.",
)
def generate_clips(
    video_path: str,
    hits: List[Dict],
    output_dir: str,
    prefix: str = "clip"
) -> Dict:
    """
    Extract video clips from search results.
    Creates clip files for each hit with timing information.
    
    Args:
        video_path: Path to the original video file
        hits: List of search hits with timing information (from search tools)
        output_dir: Directory to save the clipped video files
        prefix: Prefix for clip filenames (default: "clip")
        
    Returns:
        Dictionary with list of generated clip paths and count
    """
    try:
        # Validate video path exists
        if not os.path.exists(video_path):
            return {
                "status": "error",
                "error": f"Video file not found: {video_path}",
                "video_path": video_path
            }
        
        print(f"Generating clips from: {video_path}")
        print(f"Output directory: {output_dir}")
        print(f"Number of hits: {len(hits)}")
        
        clip_paths = get_video_clips_from_hits(
            video_path=video_path,
            hits=hits,
            output_dir=output_dir,
            prefix=prefix
        )
        return {
            "status": "success",
            "clips_generated": len(clip_paths),
            "clip_paths": clip_paths,
            "output_dir": output_dir
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "video_path": video_path
        }
    
# ===== Tool 6: Get Video Info =====
@mcp.tool(
    name="get_video_info",
    description="Get information about a processed video, including frame count and index paths.",
)
def get_video_info(video_id: str) -> Dict:
    """
    Get information about a processed video.
    Returns frame count, index paths, and collection names.
    
    Args:
        video_id: ID of the video
        
    Returns:
        Dictionary with video information and processing status
    """
    try:
        video_dir = os.path.join(storage_dir, video_id)
        frames_dir = os.path.join(video_dir, "frames")
        faiss_index_path = os.path.join(video_dir, "faiss_index.bin")
        video_info_path = os.path.join(video_dir, "video_info.json")
        
        if not os.path.exists(video_dir):
            return {
                "status": "not_found",
                "video_id": video_id,
                "message": "Video has not been processed"
            }
        
        # Load video info if available
        video_path = None
        if os.path.exists(video_info_path):
            with open(video_info_path, "r") as f:
                info = json.load(f)
                video_path = info.get("video_path")
        
        frame_count = len([
            f for f in os.listdir(frames_dir) 
            if f.endswith('.jpg')
        ]) if os.path.exists(frames_dir) else 0
        
        return {
            "status": "found",
            "video_id": video_id,
            "frame_count": frame_count,
            "faiss_index_exists": os.path.exists(faiss_index_path),
            "transcript_collection": f"video_{video_id}",
            "frames_collection": f"frames_{video_id}",
            "storage_path": video_dir,
            "video_path": video_path
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "video_id": video_id
        }
    
# ===== Tool 7: List Processed Videos =====
@mcp.tool(
    name="list_videos",
    description="List all processed videos in the storage directory.",
)
def list_videos() -> Dict:
    """
    List all processed videos in the storage directory.
    
    Returns:
        Dictionary with list of video IDs and their processing status
    """
    try:
        if not os.path.exists(storage_dir):
            return {
                "status": "success",
                "videos": [],
                "count": 0
            }
        
        videos = []
        for video_id in os.listdir(storage_dir):
            video_path = os.path.join(storage_dir, video_id)
            if os.path.isdir(video_path):
                faiss_index = os.path.join(video_path, "faiss_index.bin")
                frames_dir = os.path.join(video_path, "frames")
                
                videos.append({
                    "video_id": video_id,
                    "indexed": os.path.exists(faiss_index),
                    "frame_count": len([
                        f for f in os.listdir(frames_dir) 
                        if f.endswith('.jpg')
                    ]) if os.path.exists(frames_dir) else 0
                })
        
        return {
            "status": "success",
            "videos": videos,
            "count": len(videos)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# ===== Tool 8: Clear Storage =====
@mcp.tool(
    name="clear_storage",
    description="Clear all storage directories including frames, clips, and vector databases.",
)
def clear_storage() -> Dict:
    """
    Clear all storage directories in the MCP server.
    This includes extracted frames, ChromaDB, clips output, etc.
    
    Returns:
        Dictionary with clearing status and statistics
    """
    import shutil
    
    # Define directories to clear (relative to server.py location)
    server_dir = os.path.dirname(os.path.abspath(__file__))
    
    dirs_to_clear = [
        os.path.join(server_dir, "storage", "frames"),
        os.path.join(server_dir, "chroma_db"),
        os.path.join(server_dir, "clips_output"),
        os.path.join(server_dir, "mosaic", "extracted_frames"),
        storage_dir,  # The configured storage directory
    ]
    
    stats = {
        "status": "success",
        "directories_cleared": 0,
        "files_deleted": 0,
        "errors": []
    }
    
    try:
        for dir_path in dirs_to_clear:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                try:
                    # Count files before clearing
                    file_count = sum(1 for _ in os.walk(dir_path) for _ in _[2])
                    stats["files_deleted"] += file_count
                    
                    # Remove all contents but keep the directory
                    for item in os.listdir(dir_path):
                        item_path = os.path.join(dir_path, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                    
                    stats["directories_cleared"] += 1
                except Exception as e:
                    stats["errors"].append(f"Error clearing {dir_path}: {str(e)}")
        
        # Reinitialize search engine to clear in-memory state
        global search_engine
        search_engine = MultimodalSearchEngine(storage_dir=storage_dir)
        
        return stats
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    
# ================ Summerization Tool (Optional) ================
@mcp.tool(
    name="summarize_video",
    description="Generate a summary of the video content using its transcript.",
)
def summarize_video(video_id: str, max_length: int = 150) -> Dict:
    """
    Summarize video content using its transcript.
    
    Args:
        video_id: ID of the video to summarize
        max_length: Maximum length of the summary in words (default: 150)
        
    Returns:
        Dictionary with summary text and status
    """
    try:
        summary = search_engine.summarize_video(
            video_id=video_id,
            max_length=max_length
        )
        return {
            "status": "success",
            "video_id": video_id,
            "summary": summary
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "video_id": video_id
        }


# ============== TOOL 9: Search by Audio ==============
@mcp.tool(
    name="search_audio",
    description="Search video by audio similarity. Transcribes the uploaded audio clip and finds matching segments in the video transcript.",
)
def search_audio(audio_path: str, video_id: str, k: int = 5) -> List[Dict]:
    """
    Search video by audio similarity.
    Transcribes the query audio and searches the video transcript for matches.
    
    Args:
        audio_path: Path to the query audio file (wav, mp3, etc.)
        video_id: ID of the video to search
        k: Number of results to return (default: 5)
        
    Returns:
        List of matching transcript segments with timestamps
    """
    try:
        results = search_engine.search_audio(
            audio_path=audio_path,
            video_id=video_id,
            k=k
        )
        return results
    except Exception as e:
        return [{
            "error": str(e),
            "audio_path": audio_path,
            "video_id": video_id
        }]


# ============== MCP RESOURCES ==============
# Resources expose data to LLMs (similar to GET endpoints)

@mcp.resource("video://{video_id}/transcript")
def get_video_transcript(video_id: str) -> str:
    """
    Get the full transcript of a video.
    """
    try:
        video_dir = os.path.join(storage_dir, video_id)
        video_info_path = os.path.join(video_dir, "video_info.json")
        
        if os.path.exists(video_info_path):
            with open(video_info_path, "r") as f:
                info = json.load(f)
                return info.get("transcript", "Transcript not available")
        return f"Video {video_id} not found or not processed"
    except Exception as e:
        return f"Error reading transcript: {str(e)}"


@mcp.resource("video://{video_id}/info")
def get_video_metadata(video_id: str) -> str:
    """
    Get metadata for a processed video.
    """
    try:
        video_dir = os.path.join(storage_dir, video_id)
        frames_dir = os.path.join(video_dir, "frames")
        faiss_index_path = os.path.join(video_dir, "faiss_index.bin")
        
        if not os.path.exists(video_dir):
            return json.dumps({"status": "not_found", "video_id": video_id})
        
        frame_count = len([
            f for f in os.listdir(frames_dir) 
            if f.endswith('.jpg')
        ]) if os.path.exists(frames_dir) else 0
        
        return json.dumps({
            "video_id": video_id,
            "frame_count": frame_count,
            "indexed": os.path.exists(faiss_index_path),
            "storage_path": video_dir
        })
    except Exception as e:
        return json.dumps({"error": str(e), "video_id": video_id})


@mcp.resource("video://list")
def get_all_videos() -> str:
    """
    Get list of all processed videos.
    """
    try:
        if not os.path.exists(storage_dir):
            return json.dumps({"videos": [], "count": 0})
        
        videos = [
            video_id for video_id in os.listdir(storage_dir)
            if os.path.isdir(os.path.join(storage_dir, video_id))
        ]
        return json.dumps({"videos": videos, "count": len(videos)})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============== MCP PROMPTS ==============
# Prompts define reusable templates for LLM interactions

@mcp.prompt("summarize")
def summarize_prompt(video_id: str) -> str:
    """Generate a prompt for summarizing a video."""
    return f"""Please summarize the content of video '{video_id}'. 
Use the summarize_video tool to get the transcript summary, then provide a clear and concise overview of the main topics covered."""


@mcp.prompt("search_guidance")
def search_guidance_prompt() -> str:
    """Provide guidance on which search tool to use."""
    return """When searching video content, choose the appropriate tool:

1. **search_text** - Use when looking for spoken words or dialogue. Searches the video transcript.
   Example: "Find where they discuss machine learning"

2. **search_visual** - Use when looking for visual content. Uses CLIP embeddings for visual similarity.
   Example: "Find frames showing a red car" or "Show scenes with sunset"

3. **search_caption** - Use when looking for described scenes. Searches AI-generated frame descriptions.
   Example: "Find frames where someone is holding a phone"

After finding results, use **generate_clips** to extract video clips from the timestamps."""


@mcp.prompt("clip_workflow")
def clip_workflow_prompt(search_query: str) -> str:
    """Generate a prompt for the clip generation workflow."""
    return f"""To generate clips for "{search_query}":
1. First, search using the appropriate tool (search_text, search_visual, or search_caption)
2. Review the search results and their timestamps
3. Use generate_clips with the video_id and the search results to create the clips
4. Report the generated clip paths to the user"""


def main(transport="http", port=9090, host="127.0.0.1"):
    """Run the MCP server with HTTP or STDIO transport.
    
    HTTP transport: Uses FastMCP's streamable HTTP at /mcp endpoint
    STDIO transport: Uses standard input/output for local subprocess communication
    """
    import uvicorn
    from fastapi import FastAPI
    
    print(f"Starting Mosaic MCP Server on {host}:{port}")
    print(f"Transport: {transport}")
    
    if transport == "http":
        # Use FastMCP's native HTTP transport with custom FastAPI app
        app = FastAPI(title="Mosaic MCP Server")
        
        # Define REST endpoints FIRST (before mount) to ensure they take priority
        # These are legacy endpoints kept for backward compatibility
        @app.post("/mcp/v1/tools/process_video")
        async def handle_process_video(request: Request):
            data = await request.json()
            result = process_video(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/search_text")
        async def handle_search_text(request: Request):
            data = await request.json()
            result = search_text(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/search_image")
        async def handle_search_image(request: Request):
            data = await request.json()
            result = search_image(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/search_caption")
        async def handle_search_caption(request: Request):
            data = await request.json()
            result = search_caption(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/search_visual")
        async def handle_search_visual(request: Request):
            data = await request.json()
            result = search_visual(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/generate_clips")
        async def handle_generate_clips(request: Request):
            data = await request.json()
            result = generate_clips(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/get_video_info")
        async def handle_get_video_info(request: Request):
            data = await request.json()
            result = get_video_info(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/list_videos")
        async def handle_list_videos(request: Request):
            result = list_videos()
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/summarize_video")
        async def handle_summarize_video(request: Request):
            data = await request.json()
            result = summarize_video(**data)
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/clear_storage")
        async def handle_clear_storage(request: Request):
            result = clear_storage()
            return JSONResponse(result)

        @app.post("/mcp/v1/tools/search_audio")
        async def handle_search_audio(request: Request):
            data = await request.json()
            result = search_audio(**data)
            return JSONResponse(result)

        @app.get("/")
        async def root():
            return {
                "status": "ok", 
                "message": "Mosaic MCP Server Running", 
                "transport": "http",
                "mcp_endpoint": "/mcp"
            }
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        # Mount MCP protocol endpoint AFTER defining REST routes
        # This ensures REST routes take priority for specific paths
        mcp_app = mcp.streamable_http_app()
        app.mount("/mcp/protocol", mcp_app)

        print(f"Running HTTP transport on http://{host}:{port}")
        print("Available endpoints:")
        print("  GET  / - Server status")
        print("  GET  /health - Health check")
        print("  MCP  /mcp/protocol - Standard MCP protocol endpoint")
        print("  POST /mcp/v1/tools/* - Legacy REST endpoints")
        uvicorn.run(app, host=host, port=port)
        
    elif transport == "stdio":
        # Use FastMCP's built-in stdio transport
        print("Running STDIO transport...")
        mcp.run(transport="stdio")
    else:
        print(f"Unknown transport: {transport}. Using HTTP.")
        main(transport="http", port=port, host=host)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mosaic MCP Server")
    parser.add_argument("--port", type=int, default=9090, help="Port to run the server on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--transport", default="http", choices=["http", "stdio"], help="Transport type (http or stdio)")
    
    args = parser.parse_args()
    
    print(f"Mosaic MCP Server - {args.transport.upper()} Transport on {args.host}:{args.port}")
    
    main(transport=args.transport, port=args.port, host=args.host)
