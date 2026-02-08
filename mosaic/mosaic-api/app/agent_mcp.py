"""
VideoAgent using LangChain MCP adapters for official MCP integration.

This module provides a VideoAgent that connects to the MCP server using
the official langchain-mcp-adapters library.

Reference: https://docs.langchain.com/oss/python/langchain/mcp
"""

import asyncio
import os
import json
from typing import Dict, List, Optional

from langchain_mistralai import ChatMistralAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_community.chat_message_histories import ChatMessageHistory

from config import MCP_SERVER_URL, UPLOAD_DIR
import httpx


class MCPToolAdapter:
    """
    Adapter that wraps MCP server tools for use with LangChain agents.
    Uses HTTP transport to communicate with the MCP server's REST endpoints.
    """
    
    def __init__(self, mcp_server_url: str):
        self.base_url = mcp_server_url
        self.client = httpx.Client(timeout=120.0)
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call an MCP tool via HTTP REST endpoint."""
        url = f"{self.base_url}/mcp/v1/tools/{tool_name}"
        response = self.client.post(url, json=arguments)
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


class VideoAgentMCP:
    """
    Video analysis agent using MCP adapter for tool interactions.
    Uses LangChain ReAct agent with HTTP-based MCP tool calls.
    """
    
    def __init__(self):
        """Initialize the agent with MCP adapter."""
        # Initialize LLM
        self.llm = ChatMistralAI(
            api_key=os.getenv("MISTRAL_API_KEY", "wdRPqlYhnNnML2PVDygaSZdTgNIuug9A"),
            model='mistral-large-latest',
            temperature=0
        )
        
        # Initialize MCP adapter
        self.mcp = MCPToolAdapter(MCP_SERVER_URL)
        
        # Message history
        self.message_history = ChatMessageHistory()
        
        # Video paths for clip generation
        self.video_paths: Dict[str, str] = {}
        self._load_video_paths()
        
        # Create tools and agent
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _load_video_paths(self):
        """Load video paths from storage."""
        paths_file = os.path.join(UPLOAD_DIR, "video_paths.json")
        if os.path.exists(paths_file):
            try:
                with open(paths_file, "r") as f:
                    content = f.read().strip()
                    if content:
                        self.video_paths = json.loads(content)
            except (json.JSONDecodeError, IOError):
                self.video_paths = {}
    
    def _save_video_paths(self):
        """Save video paths to storage."""
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        paths_file = os.path.join(UPLOAD_DIR, "video_paths.json")
        with open(paths_file, "w") as f:
            json.dump(self.video_paths, f)
    
    def register_video(self, video_id: str, video_path: str):
        """Register a video path for clip generation."""
        self.video_paths[video_id] = video_path
        self._save_video_paths()
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from MCP server."""
        
        def search_text(query_and_video: str) -> str:
            """Search video transcript. Format: 'query|video_id'"""
            try:
                parts = query_and_video.split("|")
                query = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                result = self.mcp.call_tool("search_text", {
                    "query": query,
                    "video_id": video_id,
                    "k": 5
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def search_caption(query_and_video: str) -> str:
            """Search frame captions. Format: 'query|video_id'"""
            try:
                parts = query_and_video.split("|")
                query = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                result = self.mcp.call_tool("search_caption", {
                    "query": query,
                    "video_id": video_id,
                    "k": 5
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def search_visual(query_and_video: str) -> str:
            """CLIP visual search. Format: 'query|video_id'"""
            try:
                parts = query_and_video.split("|")
                query = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                result = self.mcp.call_tool("search_visual", {
                    "query": query,
                    "video_id": video_id,
                    "k": 5
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def get_video_info(video_id: str) -> str:
            """Get video metadata."""
            try:
                result = self.mcp.call_tool("get_video_info", {
                    "video_id": video_id.strip()
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def list_videos(dummy: str = "") -> str:
            """List all processed videos."""
            try:
                result = self.mcp.call_tool("list_videos", {})
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def generate_clips(params: str) -> str:
            """Generate clips. Format: 'video_id|[hits_json]'"""
            try:
                parts = params.split("|", 1)
                video_id = parts[0].strip()
                hits_json = parts[1].strip() if len(parts) > 1 else "[]"
                
                try:
                    hits = json.loads(hits_json)
                except json.JSONDecodeError:
                    import ast
                    hits = ast.literal_eval(hits_json)
                
                # Try to get video path from local cache first
                video_path = self.video_paths.get(video_id)
                
                # If not found locally, check UPLOAD_DIR
                if not video_path or not os.path.exists(video_path):
                    for f in os.listdir(UPLOAD_DIR):
                        if f.startswith(video_id):
                            video_path = os.path.abspath(os.path.join(UPLOAD_DIR, f))
                            self.register_video(video_id, video_path)
                            break
                
                # If still not found, get from MCP server's get_video_info
                if not video_path or not os.path.exists(video_path):
                    info = self.mcp.call_tool("get_video_info", {"video_id": video_id})
                    if info.get("status") == "found" and info.get("video_path"):
                        video_path = info["video_path"]
                        if os.path.exists(video_path):
                            self.register_video(video_id, video_path)
                
                if not video_path or not os.path.exists(video_path):
                    return f"Error: Video file not found for {video_id}. Path: {video_path}"
                
                output_dir = os.path.abspath(os.path.join("clips_output", video_id))
                result = self.mcp.call_tool("generate_clips", {
                    "video_path": video_path,
                    "hits": hits,
                    "output_dir": output_dir
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def summarize_video(video_id: str) -> str:
            """Summarize video content."""
            try:
                result = self.mcp.call_tool("summarize_video", {
                    "video_id": video_id.strip(),
                    "max_length": 150
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def search_by_image(params: str) -> str:
            """Search video by image similarity. Format: 'image_path|video_id'"""
            try:
                parts = params.split("|")
                image_path = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                
                # Search with more results initially for filtering
                result = self.mcp.call_tool("search_image", {
                    "query_image_path": image_path,
                    "video_id": video_id,
                    "k": 5
                })
                
                # Similarity threshold - lower distance = more similar
                # CLIP distance typically ranges 0-20+
                # Threshold of 12 means good visual similarity
                SIMILARITY_THRESHOLD = 15.0
                
                # Filter results by threshold
                if isinstance(result, list):
                    filtered = [hit for hit in result if hit.get("distance", 999) < SIMILARITY_THRESHOLD]
                    
                    if not filtered:
                        return json.dumps({
                            "status": "no_match",
                            "message": f"No visually similar frames found. Best match had distance {result[0].get('distance', 'N/A'):.2f} (threshold: {SIMILARITY_THRESHOLD})",
                            "results": []
                        })
                    
                    return json.dumps(filtered, indent=2)
                
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def search_by_audio(params: str) -> str:
            """Search video by audio similarity. Format: 'audio_path|video_id'"""
            try:
                parts = params.split("|")
                audio_path = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                result = self.mcp.call_tool("search_audio", {
                    "audio_path": audio_path,
                    "video_id": video_id,
                    "k": 3
                })
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error: {str(e)}"
        
        return [
            Tool(name="search_transcript", func=search_text,
                 description="Search video transcript. Format: 'query|video_id'"),
            Tool(name="search_frames", func=search_caption,
                 description="Search frame captions. Format: 'description|video_id'"),
            Tool(name="search_visual", func=search_visual,
                 description="CLIP visual search. Format: 'description|video_id'"),
            Tool(name="search_by_image", func=search_by_image,
                 description="Search video using an uploaded image for visual similarity. Format: 'image_path|video_id'"),
            Tool(name="search_by_audio", func=search_by_audio,
                 description="Search video using an uploaded audio clip for audio similarity. Format: 'audio_path|video_id'"),
            Tool(name="get_video_info", func=get_video_info,
                 description="Get video metadata. Input: video_id"),
            Tool(name="list_videos", func=list_videos,
                 description="List all processed videos."),
            Tool(name="generate_clips", func=generate_clips,
                 description="Generate clips. Format: 'video_id|[hits]'"),
            Tool(name="summarize_video", func=summarize_video,
                 description="Summarize video. Input: video_id"),
        ]
    
    def _handle_parsing_error(self, error: Exception) -> str:
        """Handle LLM parsing errors."""
        import re
        error_str = str(error)
        if "Could not parse LLM output:" in error_str:
            match = re.search(r'Could not parse LLM output: `(.+?)`', error_str, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                if extracted and not extracted.startswith("Action:") and len(extracted) > 20:
                    return f"Final Answer: {extracted}"
        return "Format error. Use 'Thought:' + 'Action:' + 'Action Input:', or 'Final Answer:'."
    
    def _create_agent(self) -> AgentExecutor:
        """Create ReAct agent with tools."""
        prompt = PromptTemplate.from_template(
            """You are a video analysis assistant with MCP-powered tools.

Available tools:
{tools}

Tool names: {tool_names}

WORKFLOW:
1. Spoken content: search_transcript with 'query|video_id'
2. Visual content: search_visual with 'description|video_id' (uses CLIP)
3. Described scenes: search_frames with 'description|video_id'
4. Image search: search_by_image with 'image_path|video_id' (user uploaded image)
5. Audio search: search_by_audio with 'audio_path|video_id' (user uploaded audio)
6. Clips: First search, then generate_clips with ONLY the single best (highest relevance) result
7. Summary: summarize_video with video_id

IMPORTANT CLIP RULE:
- When generating clips, ALWAYS pick ONLY the top 1 most relevant search result
- Pass only that single best hit to generate_clips, never more than one
- Example: generate_clips with 'video_id|[single_best_hit]'

IMAGE/AUDIO SEARCH:
- If the message contains "[User uploaded an image for visual search: <path>]", use search_by_image with that exact path
- If the message contains "[User uploaded an audio clip for audio search: <path>]", use search_by_audio with that exact path
- search_by_image has a similarity threshold - if the result has "status": "no_match", tell the user no similar frames were found
- Only generate clips if similar frames are found (non-empty results)
- After getting valid results, pick the BEST match and generate ONE clip

FORMAT:
Thought: <reasoning>
Action: <tool_name>
Action Input: <input>

OR

Thought: I now know the final answer
Final Answer: <answer>

RULES:
- Never write "Observation:" yourself
- Stop after Action Input
- Use video_id from context [Video ID: xxx]

Question: {input}
{agent_scratchpad}"""
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=self._handle_parsing_error,
            early_stopping_method="generate"
        )
    
    def chat(self, message: str, video_id: str = None) -> Dict:
        """Process user message through agent."""
        try:
            context = f"[Video ID: {video_id}] " if video_id else ""
            response = self.agent.invoke({"input": context + message})
            return {"response": response["output"], "success": True}
        except Exception as e:
            return {"response": f"Error: {str(e)}", "success": False}
    
    def reset_memory(self):
        """Clear conversation history."""
        self.message_history.clear()


# Alias for backward compatibility
VideoAgent = VideoAgentMCP
