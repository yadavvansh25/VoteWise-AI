import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.gemini_service import GeminiService

@pytest.fixture
def gemini_service():
    return GeminiService()

@patch('app.services.gemini_service.genai')
@pytest.mark.asyncio
async def test_gemini_service_generate_response_no_key(mock_google_genai, gemini_service):
    gemini_service._api_key = None
    
    response = await gemini_service.generate_response(
        message="Test",
        intent="general",
        language="en",
        conversation_history=[],
        use_grounding=False
    )
    assert response["grounding_metadata"] is False
    assert "apologize" in response["text"].lower() or "voters.eci.gov.in" in response["text"].lower()

@patch('app.services.gemini_service.genai')
@pytest.mark.asyncio
async def test_gemini_service_generate_response_with_key(mock_genai, gemini_service):
    gemini_service._api_key = "FAKE_KEY"
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_response = MagicMock()
    mock_response.text = "This is a real candidate response."
    
    # Mock grounding metadata
    mock_chunk = MagicMock()
    mock_chunk.web.title = "Source Title"
    mock_chunk.web.uri = "http://example.com"
    mock_grounding = MagicMock()
    mock_grounding.grounding_chunks = [mock_chunk]
    
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].grounding_metadata = mock_grounding
    
    mock_client.models.generate_content.return_value = mock_response
    
    response = await gemini_service.generate_response(
        message="Who is running?",
        intent="candidate_info",
        language="en",
        conversation_history=[],
        use_grounding=True
    )
    
    print(response)
    assert response["text"] == "This is a real candidate response."
    assert len(response["sources"]) == 1
    assert response["sources"][0]["title"] == "Source Title"

@patch('app.services.gemini_service.genai')
@pytest.mark.asyncio
async def test_gemini_service_exception_handling(mock_genai, gemini_service):
    gemini_service._api_key = "FAKE_KEY"
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_client.models.generate_content.side_effect = Exception("API failure")
    
    response = await gemini_service.generate_response(
        message="Crash test",
        intent="general",
        language="en",
        conversation_history=[],
        use_grounding=False
    )
    
    assert "error" in response["text"].lower() or "trouble" in response["text"].lower()
