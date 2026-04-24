"""
VoteWise AI — Gemini 1.5 Flash Service
Client wrapper for Google's Gemini 1.5 Flash model with Search Grounding.
"""

import logging
from typing import List, Optional, Dict, Any

from google import genai
from google.genai import types

from app.config import get_settings
from app.services.election_data import get_system_prompt, get_knowledge_context

logger = logging.getLogger("votewise.gemini")


class GeminiService:
    """Wrapper for Google Gemini 1.5 Flash API with Search Grounding support."""

    def __init__(self, api_key: str = None):
        settings = get_settings()
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model = settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        """Lazily initialize the Gemini client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError(
                    "GEMINI_API_KEY is not set. Please set it in your .env file."
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate_response(
        self,
        message: str,
        intent: str = "general",
        language: str = "en",
        conversation_history: List[Dict[str, str]] = None,
        use_grounding: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini 1.5 Flash.

        Args:
            message: The user's message.
            intent: Classified intent for prompt customization.
            language: Target response language.
            conversation_history: Previous conversation messages.
            use_grounding: Whether to enable Google Search Grounding.

        Returns:
            Dict with 'text', 'sources', and 'grounding_metadata' keys.
        """
        try:
            client = self._get_client()

            # Build system prompt
            system_prompt = get_system_prompt(intent, language)
            knowledge_context = get_knowledge_context(intent)

            # Build the full prompt with context
            full_system = system_prompt + knowledge_context

            # Build conversation contents
            contents = []

            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 6 messages for context
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part(text=msg.get("content", ""))],
                        )
                    )

            # Add current message
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=message)],
                )
            )

            # Configure tools (Search Grounding for candidate queries)
            config_kwargs = {
                "system_instruction": full_system,
                "temperature": 0.7,
                "max_output_tokens": 2048,
            }

            if use_grounding:
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
                config_kwargs["tools"] = [grounding_tool]

            config = types.GenerateContentConfig(**config_kwargs)

            # Generate response
            response = client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

            # Extract response text
            response_text = response.text if response.text else ""

            # Extract grounding sources
            sources = []
            if use_grounding and response.candidates:
                candidate = response.candidates[0]
                grounding_meta = getattr(candidate, "grounding_metadata", None)
                if grounding_meta:
                    chunks = getattr(grounding_meta, "grounding_chunks", [])
                    if chunks:
                        for chunk in chunks:
                            web = getattr(chunk, "web", None)
                            if web:
                                sources.append({
                                    "title": getattr(web, "title", "Source"),
                                    "url": getattr(web, "uri", ""),
                                    "snippet": None,
                                })

            logger.info(
                "Gemini response generated: intent=%s, language=%s, "
                "grounded=%s, sources=%d",
                intent, language, use_grounding, len(sources),
            )

            return {
                "text": response_text,
                "sources": sources,
                "grounding_metadata": bool(sources),
            }

        except Exception as e:
            logger.error("Gemini API error: %s", str(e))
            return {
                "text": _get_fallback_response(language),
                "sources": [],
                "grounding_metadata": False,
                "error": str(e),
            }


def _get_fallback_response(language: str) -> str:
    """Get a fallback response when Gemini is unavailable."""
    fallbacks = {
        "en": (
            "I apologize, but I'm having trouble connecting to my knowledge service "
            "right now. Please try again in a moment. In the meantime, you can visit "
            "the official Election Commission portal at **voters.eci.gov.in** or "
            "call the Voter Helpline at **1950** for immediate assistance."
        ),
        "hi": (
            "मुझे खेद है, लेकिन मुझे अभी अपनी ज्ञान सेवा से जुड़ने में समस्या हो रही है। "
            "कृपया कुछ देर बाद पुनः प्रयास करें। इस बीच, आप आधिकारिक चुनाव आयोग पोर्टल "
            "**voters.eci.gov.in** पर जा सकते हैं या तत्काल सहायता के लिए "
            "वोटर हेल्पलाइन **1950** पर कॉल कर सकते हैं।"
        ),
        "ta": (
            "மன்னிக்கவும், இப்போது என் அறிவுச் சேவையுடன் இணைவதில் சிரமம் ஏற்பட்டுள்ளது. "
            "சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும். இதற்கிடையில், அதிகாரப்பூர்வ "
            "தேர்தல் ஆணைய இணையதளம் **voters.eci.gov.in** அல்லது "
            "வாக்காளர் உதவி எண் **1950** ஐ அழைக்கவும்."
        ),
    }
    return fallbacks.get(language, fallbacks["en"])


# Global singleton
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the global GeminiService instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
