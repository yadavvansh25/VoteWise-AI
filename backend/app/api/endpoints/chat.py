"""
VoteWise AI — Chat Endpoint
Main conversation endpoint with full processing pipeline.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import (
    ChatRequest, ChatResponse, Intent, SourceCitation, PIIDetectionInfo
)
from app.core.intent import classify_intent
from app.core.bias_filter import filter_response
from app.core.cache import get_cached_answer, cache_answer
from app.core.security import redact_pii, get_pii_warning_message
from app.services.gemini_service import get_gemini_service
from app.core.rate_limiter import limiter

logger = logging.getLogger("votewise.chat")
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint. Processing pipeline:
    1. PII Redaction (already done by middleware, but double-check)
    2. Cache lookup
    3. Intent classification
    4. Gemini API call (with grounding for candidate queries)
    5. Bias filter
    6. Cache storage
    7. Response formatting
    """
    try:
        message = body.message
        language = body.language.value

        # --- Step 1: PII Redaction (defense-in-depth) ---
        redacted_message, pii_types = redact_pii(message)
        pii_info = PIIDetectionInfo(detected=False)

        if pii_types:
            pii_info = PIIDetectionInfo(
                detected=True,
                types=pii_types,
                message=get_pii_warning_message(pii_types, language),
            )
            message = redacted_message
            logger.info("PII redacted at endpoint level: %s", pii_types)

        # --- Step 2: Intent Classification ---
        intent, confidence = classify_intent(message)
        logger.info(
            "Intent classified: %s (confidence=%.2f)", intent.value, confidence
        )

        # --- Step 3: Cache Lookup ---
        cached = await get_cached_answer(message, language)
        if cached:
            logger.info("Cache hit for message")
            response_text = cached

            # Still apply bias filter on cached content
            response_text, was_filtered = filter_response(
                message, response_text, language
            )

            return ChatResponse(
                message=response_text,
                intent=intent,
                language=body.language,
                sources=[],
                pii_info=pii_info,
                cached=True,
            )

        # --- Step 4: Bias Pre-Check ---
        from app.core.bias_filter import check_partisan_request, NEUTRAL_REFUSAL_MESSAGES
        if check_partisan_request(message):
            refusal = NEUTRAL_REFUSAL_MESSAGES.get(language, NEUTRAL_REFUSAL_MESSAGES["en"])
            return ChatResponse(
                message=refusal,
                intent=intent,
                language=body.language,
                sources=[],
                pii_info=pii_info,
                cached=False,
            )

        # --- Step 5: Gemini API Call ---
        use_grounding = intent == Intent.CANDIDATE_INFO
        gemini = get_gemini_service()

        # Build conversation history for context
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in body.conversation_history
        ]

        result = await gemini.generate_response(
            message=message,
            intent=intent.value,
            language=language,
            conversation_history=history,
            use_grounding=use_grounding,
        )

        response_text = result.get("text", "")

        # --- Step 6: Bias Post-Filter ---
        response_text, was_filtered = filter_response(
            message, response_text, language
        )

        if was_filtered:
            logger.warning("Response was filtered by bias check")

        # --- Step 7: Format Sources ---
        sources = [
            SourceCitation(
                title=src.get("title", "Source"),
                url=src.get("url", ""),
                snippet=src.get("snippet"),
            )
            for src in result.get("sources", [])
        ]

        # --- Step 8: Cache Storage ---
        if not was_filtered and response_text:
            await cache_answer(
                question=message,
                answer=response_text,
                language=language,
                intent=intent.value,
            )

        # --- Step 9: Build Response ---
        # Prepend PII warning if needed
        final_message = response_text
        if pii_info.detected and pii_info.message:
            final_message = f"{pii_info.message}\n\n---\n\n{response_text}"

        return ChatResponse(
            message=final_message,
            intent=intent,
            language=body.language,
            sources=sources,
            pii_info=pii_info,
            cached=False,
        )

    except Exception as e:
        logger.error("Chat endpoint error: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again.",
        )
