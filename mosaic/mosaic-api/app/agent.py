from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from mcp_client import MCPClient
from config import GROQ_API_KEY, LLM_MODEL, MCP_SERVER_URL
from typing import Dict, List

class VideoAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=0
        )
        self.mcp_client = MCPClient(MCP_SERVER_URL)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from MCP server capabilities."""
        
        def search_transcript(query_and_video: str) -> str:
            """Search video transcript. Input: 'query|video_id'"""
            query, video_id = query_and_video.split("|")
            results = self.mcp_client.search_text(query.strip(), video_id.strip())
            return str(results)
        
        def search_frames_by_text(query_and_video: str) -> str:
            """Search video frames by caption. Input: 'query|video_id'"""
            query, video_id = query_and_video.split("|")
            results = self.mcp_client.search_caption(query.strip(), video_id.strip())
            return str(results)
        
        def get_video_information(video_id: str) -> str:
            """Get information about a processed video."""
            result = self.mcp_client.get_video_info(video_id)
            return str(result)
        
        def list_all_videos(dummy: str = "") -> str:
            """List all available processed videos."""
            result = self.mcp_client.list_videos()
            return str(result)
        
        return [
            Tool(
                name="search_transcript",
                func=search_transcript,
                description="Search video transcript for spoken content. Use format: 'search query|video_id'"
            ),
            Tool(
                name="search_frames",
                func=search_frames_by_text,
                description="Search video frames by visual content description. Use format: 'description|video_id'"
            ),
            Tool(
                name="get_video_info",
                func=get_video_information,
                description="Get processing status and metadata for a video. Input: video_id"
            ),
            Tool(
                name="list_videos",
                func=list_all_videos,
                description="List all processed videos in the system."
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create ReAct agent with tools."""
        prompt = PromptTemplate.from_template(
            """You are a helpful video analysis assistant. You have access to tools for searching video content.
            
Available tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
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
        self.memory.clear()
