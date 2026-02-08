from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from mcp_client import MCPClient
from config import GROQ_API_KEY, LLM_MODEL,MISTRAL_API_KEY, MCP_SERVER_URL, GEMINI_API_KEY, UPLOAD_DIR
from typing import Dict, List
import os
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path="mosaic\.env")

class VideoAgent:
    def __init__(self):
        # Use Gemini which works better with ReAct text-based agents
        # self.llm = ChatGoogleGenerativeAI(
        #     api_key=os.getenv("GEMINI_API_KEY", GEMINI_API_KEY),
        #     model='gemini-2.0-flash',
        #     temperature=0
        # )
        self.llm = ChatMistralAI(
            api_key= os.getenv("MISTRAL_API_KEY") or MISTRAL_API_KEY,
            model='mistral-large-latest',
            temperature=0
        )
        # Alternative: Groq (may have tool choice issues with some models)
        # self.llm = ChatGroq(
        #     api_key=os.getenv("GROQ_API_KEY") or GROQ_API_KEY,
        #     model='llama-3.3-70b-versatile',  # Use Llama which works better with ReAct
        #     temperature=0
        # )
        self.mcp_client = MCPClient(MCP_SERVER_URL)
        self.message_history = ChatMessageHistory()
        # Store video_id -> video_path mapping for clip generation
        self.video_paths: Dict[str, str] = {}
        self._load_video_paths()
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
                    else:
                        self.video_paths = {}
            except json.JSONDecodeError:
                # Handle corrupted JSON file
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
        """Create LangChain tools from MCP server capabilities."""
        
        def search_transcript(query_and_video: str) -> str:
            """Search video transcript. Input: 'query|video_id'"""
            try:
                parts = query_and_video.split("|")
                query = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                results = self.mcp_client.search_text(query, video_id)
                return str(results)
            except Exception as e:
                return f"Error searching transcript: {str(e)}"
        
        def search_frames_by_text(query_and_video: str) -> str:
            """Search video frames by AI-generated caption. Input: 'query|video_id'"""
            try:
                parts = query_and_video.split("|")
                query = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                results = self.mcp_client.search_caption(query, video_id)
                return str(results)
            except Exception as e:
                return f"Error searching frames by caption: {str(e)}"
        
        def search_visual_content(query_and_video: str) -> str:
            """Search video frames using CLIP visual similarity. Input: 'query|video_id'"""
            try:
                parts = query_and_video.split("|")
                query = parts[0].strip()
                video_id = parts[1].strip() if len(parts) > 1 else ""
                results = self.mcp_client.search_visual(query, video_id)
                return str(results)
            except Exception as e:
                return f"Error searching visual content: {str(e)}"
        
        def get_video_information(video_id: str) -> str:
            """Get information about a processed video."""
            result = self.mcp_client.get_video_info(video_id.strip())
            return str(result)
        
        def list_all_videos(dummy: str = "") -> str:
            """List all available processed videos."""
            result = self.mcp_client.list_videos()
            return str(result)
        
        def generate_video_clips(params: str) -> str:
            """
            Generate video clips from search results.
            Input format: 'video_id|hits_json'
            Where hits_json is the JSON string of search results containing timestamps.
            """
            try:
                parts = params.split("|", 1)
                video_id = parts[0].strip()
                hits_json = parts[1].strip() if len(parts) > 1 else "[]"
                
                # Parse the hits JSON
                import ast
                try:
                    hits = json.loads(hits_json)
                except:
                    hits = ast.literal_eval(hits_json)
                
                # Get video path
                video_path = self.video_paths.get(video_id)
                if not video_path or not os.path.exists(video_path):
                    # Try to find the video in uploads directory
                    try:
                        for f in os.listdir(UPLOAD_DIR):
                            if f.startswith(video_id):
                                video_path = os.path.abspath(os.path.join(UPLOAD_DIR, f))
                                # Cache this path for future use
                                self.register_video(video_id, video_path)
                                break
                    except Exception as e:
                        return f"Error listing upload directory: {str(e)}"
                
                if not video_path or not os.path.exists(video_path):
                    return f"Error: Video file not found for video_id: {video_id}. UPLOAD_DIR: {UPLOAD_DIR}"
                
                # Ensure video_path is absolute
                video_path = os.path.abspath(video_path)
                
                # Use absolute path for output directory (in API's clips_output folder)
                output_dir = os.path.abspath(os.path.join("clips_output", video_id))
                result = self.mcp_client.generate_clips(video_path, hits, output_dir)
                return str(result)
            except Exception as e:
                return f"Error generating clips: {str(e)}"
        
        def summarize_video_content(video_id: str) -> str:
            """Summarize the video content using its transcript."""
            try:
                # Get transcript by searching with broad query
                result = self.mcp_client.call_tool("summarize_video", {
                    "video_id": video_id.strip(),
                    "max_length": 150
                })
                return str(result)
            except Exception as e:
                return f"Error summarizing video: {str(e)}"
        
        return [
            Tool(
                name="search_transcript",
                func=search_transcript,
                description="Search video transcript for spoken words/dialogue. Returns matching segments with start/end timestamps. Use format: 'search query|video_id'. Use this when looking for what was SAID in the video."
            ),
            Tool(
                name="search_frames",
                func=search_frames_by_text,
                description="Search video frames by AI-generated captions. Good for finding described content. Use format: 'description|video_id'. Use for specific objects/actions mentioned in captions."
            ),
            Tool(
                name="search_visual",
                func=search_visual_content,
                description="Search video frames using CLIP visual-semantic search. Best for finding visual content that matches a description. Use format: 'visual description|video_id'. More accurate for visual similarity."
            ),
            Tool(
                name="get_video_info",
                func=get_video_information,
                description="Get processing status and metadata for a video including frame count. Input: video_id"
            ),
            Tool(
                name="list_videos",
                func=list_all_videos,
                description="List all processed videos in the system with their IDs."
            ),
            Tool(
                name="generate_clips",
                func=generate_video_clips,
                description="Generate video clips from search results. Use AFTER searching to extract clips. Input format: 'video_id|[{search_result_with_timestamps}]'. Pass the raw search results as JSON."
            ),
            Tool(
                name="summarize_video",
                func=summarize_video_content,
                description="Get a summary of the video content based on its transcript. Input: video_id"
            )
        ]
    
    def _handle_parsing_error(self, error: Exception) -> str:
        """Custom handler for parsing errors that extracts useful content."""
        error_str = str(error)
        
        # Try to extract the actual answer from malformed output
        if "Could not parse LLM output:" in error_str:
            # Extract the content after "Could not parse LLM output:"
            import re
            match = re.search(r'Could not parse LLM output: `(.+?)`', error_str, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                # If it looks like a valid answer (not an action), return it
                if extracted and not extracted.startswith("Action:") and len(extracted) > 20:
                    return f"Final Answer: {extracted}"
        
        return "Please format your response correctly. Use 'Thought:' followed by 'Action:' and 'Action Input:', OR 'Thought: I now know the final answer' followed by 'Final Answer:'. Never generate 'Observation:' yourself."
    
    def _create_agent(self) -> AgentExecutor:
        """Create ReAct agent with tools."""
        prompt = PromptTemplate.from_template(
            """You are a helpful video analysis assistant. You can search videos and generate clips.

Available tools:
{tools}

WORKFLOW FOR COMMON TASKS:

1. Finding spoken content: Use search_transcript with 'query|video_id'
2. Finding visual scenes (by caption): Use search_frames with 'description|video_id'
3. Finding visual scenes (by visual similarity): Use search_visual with 'description|video_id' - MORE ACCURATE for visual content
4. Getting clips: FIRST search (transcript, frames, or visual), THEN use generate_clips with the results
5. Summarizing: Use summarize_video with video_id

CHOOSING BETWEEN search_frames and search_visual:
- search_frames: Searches AI-generated text captions of frames. Good when looking for specific described objects.
- search_visual: Uses CLIP embeddings for visual similarity. Better for finding visually similar content.

WHEN USER ASKS FOR CLIPS:
- First search for the relevant content using search_transcript or search_frames
- Then call generate_clips with the video_id and the search results
- The search results contain timestamps needed for clip generation

CRITICAL FORMAT RULES - READ CAREFULLY:
1. NEVER write "Observation:" - the system adds this automatically after your action runs.
2. After using a tool, STOP and wait. Do NOT continue writing after "Action Input:".
3. When you have enough information, write "Thought: I now know the final answer" then "Final Answer: <your answer>".
4. Do NOT use markdown, bold, code blocks, or any special formatting.
5. When the video_id is provided in the context like [Video ID: xxx], use that video_id.

CORRECT FORMAT (follow exactly):

To use a tool (must be one of [{tool_names}]):
Thought: <your reasoning>
Action: <tool_name>
Action Input: <tool_input>

To give final answer (ONLY after you have the information you need):
Thought: I now know the final answer
Final Answer: <your complete answer to the user>

WRONG (never do this):
- Writing "Observation:" yourself
- Writing both Action and Final Answer in same response
- Continuing after Action Input

Begin!

Question: {input}
{agent_scratchpad}"""
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=self._handle_parsing_error
        )
    
    def chat(self, message: str, video_id: str = None) -> Dict:
        """Process user message through agent."""
        try:
            context = f"[Video ID: {video_id}] " if video_id else ""
            response = self.agent.invoke({"input": context + message})
            
            return {
                "response": response["output"],
                "success": True
            }
        except Exception as e:
            return {
                "response": f"Error processing request: {str(e)}",
                "success": False
            }
    
    def reset_memory(self):
        """Clear conversation history."""
        self.message_history.clear()
