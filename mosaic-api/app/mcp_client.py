import requests
from typing import Dict, List, Any, Optional

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool via HTTP."""
        url = f"{self.base_url}/mcp/v1/tools/{tool_name}"
        response = self.session.post(url, json=arguments)
        response.raise_for_status()
        return response.json()
    
    def process_video(self, video_path: str, video_id: str) -> Dict:
        """Process video through MCP server."""
        return self.call_tool("process_video", {
            "video_path": video_path,
            "video_id": video_id
        })
    
    def search_text(self, query: str, video_id: str, k: int = 5) -> List[Dict]:
        """Search transcript by text."""
        return self.call_tool("search_text", {
            "query": query,
            "video_id": video_id,
            "k": k
        })
    
    def search_image(self, query_image_path: str, video_id: str, k: int = 5) -> List[Dict]:
        """Search frames by image similarity."""
        return self.call_tool("search_image", {
            "query_image_path": query_image_path,
            "video_id": video_id,
            "k": k
        })
    
    def search_caption(self, query: str, video_id: str, k: int = 5) -> List[Dict]:
        """Search frames by caption."""
        return self.call_tool("search_caption", {
            "query": query,
            "video_id": video_id,
            "k": k
        })
    
    def search_visual(self, query: str, video_id: str, k: int = 5) -> List[Dict]:
        """Search frames by visual content using CLIP embeddings."""
        return self.call_tool("search_visual", {
            "query": query,
            "video_id": video_id,
            "k": k
        })
    
    def generate_clips(self, video_path: str, hits: List[Dict], output_dir: str) -> Dict:
        """Generate video clips from search results."""
        return self.call_tool("generate_clips", {
            "video_path": video_path,
            "hits": hits,
            "output_dir": output_dir
        })
    
    def get_video_info(self, video_id: str) -> Dict:
        """Get video processing information."""
        return self.call_tool("get_video_info", {
            "video_id": video_id
        })
    
    def list_videos(self) -> Dict:
        """List all processed videos."""
        return self.call_tool("list_videos", {})
    
    def clear_storage(self) -> Dict:
        """Clear all storage directories including frames, clips, and vector databases."""
        return self.call_tool("clear_storage", {})
    
    def search_audio(self, audio_path: str, video_id: str, k: int = 5) -> List[Dict]:
        """Search video by audio similarity."""
        return self.call_tool("search_audio", {
            "audio_path": audio_path,
            "video_id": video_id,
            "k": k
        })
