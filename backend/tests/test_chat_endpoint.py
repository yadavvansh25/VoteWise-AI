import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_gemini():
    with patch('app.api.endpoints.chat.get_gemini_service') as mock:
        service_instance = AsyncMock()
        service_instance.generate_response.return_value = {
            "text": "This is a mock response from Gemini.",
            "sources": [],
            "grounding_metadata": False
        }
        mock.return_value = service_instance
        yield service_instance

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    from app.models.database import get_database, reset_database, close_database
    await reset_database()
    await get_database("./test_votewise.db")
    yield
    await close_database()
    import os
    if os.path.exists("./test_votewise.db"):
        os.remove("./test_votewise.db")

def test_chat_endpoint_basic(mock_gemini):
    response = client.post("/api/chat", json={
        "message": "How to vote?",
        "language": "en",
        "conversation_history": []
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "This is a mock response from Gemini."
    assert data["intent"] == "process_education"
    assert data["pii_info"]["detected"] == False

@patch('app.core.security._verhoeff_checksum', return_value=True)
def test_chat_endpoint_pii_redaction(mock_verhoeff, mock_gemini):
    response = client.post("/api/chat", json={
        "message": "My aadhaar is 2345 6789 1234. How to vote?",
        "language": "en",
        "conversation_history": []
    })
    assert response.status_code == 200
    data = response.json()
    # It should have PII warning prepended
    assert "⚠️ For your security" in data["message"]
    assert "Aadhaar" in data["message"]
    assert "This is a mock response from Gemini" in data["message"]
    assert data["pii_info"]["detected"] == True
    assert "aadhaar" in data["pii_info"]["types"]
    
    # Check what was passed to gemini
    args, kwargs = mock_gemini.generate_response.call_args
    assert "2345" not in kwargs["message"]
    assert "[AADHAAR_REDACTED]" in kwargs["message"]

def test_chat_endpoint_bias_filter():
    response = client.post("/api/chat", json={
        "message": "Who should I vote for?",
        "language": "en",
        "conversation_history": []
    })
    assert response.status_code == 200
    data = response.json()
    assert "neutral election education assistant" in data["message"]
    assert "cannot recommend" in data["message"]
