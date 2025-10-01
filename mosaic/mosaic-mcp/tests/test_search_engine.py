"""
Tests for search engine
"""

import pytest
from src.vectordb.search_engine import search_engine
from src.models.schemas import SearchQuery
from src.constants import SearchType

@pytest.mark.asyncio
async def test_text_search():
    """Test text search functionality"""
    query = SearchQuery(query="test", query_type=SearchType.TEXT, top_k=5)
    results = await search_engine.search(query)
    assert isinstance(results, list)
