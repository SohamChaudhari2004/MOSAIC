"""
Tests for MCP tools
"""

import pytest
from src.tools.search_tools import search_text

@pytest.mark.asyncio
async def test_search_text_tool():
    """Test search text MCP tool"""
    result = await search_text("test query", top_k=5)
    assert "success" in result
