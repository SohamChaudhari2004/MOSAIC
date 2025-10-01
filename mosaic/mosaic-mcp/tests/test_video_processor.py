"""
Tests for video processor
"""

import pytest
from src.core.video_processor import video_processor

@pytest.mark.asyncio
async def test_video_metadata_creation(sample_video_path):
    """Test video metadata creation"""
    metadata = await video_processor._create_video_metadata(sample_video_path, "test_id")
    assert metadata is not None
    assert metadata.video_id == "test_id"
