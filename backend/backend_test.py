"""
Basic tests for the eDiscovery backend
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import after path is set
    from server import app
    client = TestClient(app)
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed")
    sys.exit(1)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ediscovery_process_endpoint_exists():
    """Test that the ediscovery process endpoint exists"""
    # Should return 422 without proper data, not 404
    response = client.post("/api/ediscovery/process", json={})
    assert response.status_code in [422, 400]  # Bad request, not not found


def test_api_docs_available():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])