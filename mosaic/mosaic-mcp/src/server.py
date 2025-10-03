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
from dotenv import load_dotenv
from typing import List, Dict, Optional
from video_processor import VideoProcessingPipeline
from search_engine import MultimodalSearchEngine , get_video_clips_from_hits

load_dotenv()

mcp = FastMCP(
    name="mosaic-mcp-server",
    instructions="This is the Mosaic MCP server for video analysis and processing. Use proper tools for different tasks as per the instructions.",
)

storage_dir = os.getenv("STORAGE_DIR", "mosaic/extracted_frames")
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
    description="Search for relevant frames in the video using a text caption query and return relevant clips.",
)
def search_caption(
    query: str, 
    video_id: str, 
    k: int = 5, 
    fps: float = 30.0
) -> List[Dict]:
    """
    Search video frame captions using text query.
    Returns matching frames with clip timing parameters.
    
    Args:
        query: Text query to search in frame captions
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
        
        if not os.path.exists(video_dir):
            return {
                "status": "not_found",
                "video_id": video_id,
                "message": "Video has not been processed"
            }
        
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
            "storage_path": video_dir
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
    


def main(transport="streamable-http", port=9090, host="127.0.0.1"):
    import uvicorn
    
    print(f"Starting Mosaic MCP Server on {host}:{port}")
    
    if transport == "streamable-http":
        # Get the FastAPI app from FastMCP and run it with custom port
        app = mcp.streamable_http_app()
        print(f"Running streamable-http transport on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
    else:
        # For other transports, use the default FastMCP run method
        print(f"Using FastMCP default configuration for transport: {transport}")
        mcp.run(transport=transport)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mosaic MCP Server")
    parser.add_argument("--port", type=int, default=9090, help="Port to run the server on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--transport", default="streamable-http", help="Transport type")
    
    args = parser.parse_args()
    
    print(f"Mosaic MCP Server - Requested: {args.host}:{args.port}")
    
    # uvicorn.run is synchronous, so we don't need asyncio.run
    main(transport=args.transport, port=args.port, host=args.host)