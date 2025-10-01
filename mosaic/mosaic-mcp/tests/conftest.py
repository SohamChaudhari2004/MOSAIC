"""
Pytest configuration and fixtures
"""

import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_video_path():
    """Sample video path for testing"""
    return "tests/data/sample_video.mp4"
