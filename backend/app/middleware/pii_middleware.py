"""
VoteWise AI — PII Redaction Middleware
FastAPI middleware that intercepts requests and redacts PII before processing.
"""

import json
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.security import redact_pii, detect_pii

logger = logging.getLogger("votewise.pii_middleware")


class PIIRedactionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that scans incoming request bodies for PII
    and redacts it before the request reaches the route handler.

    Only processes POST requests to /api/chat to avoid overhead
    on non-sensitive endpoints.
    """

    PROTECTED_PATHS = {"/api/chat"}

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Only process protected endpoints
        if request.method == "POST" and request.url.path in self.PROTECTED_PATHS:
            try:
                # Read the request body
                body_bytes = await request.body()
                body_text = body_bytes.decode("utf-8")
                body_json = json.loads(body_text)

                # Check for PII in the message field
                if "message" in body_json:
                    original_message = body_json["message"]
                    detections = detect_pii(original_message)

                    if detections:
                        redacted_message, pii_types = redact_pii(original_message)
                        body_json["message"] = redacted_message

                        # Store PII info in request state for the endpoint
                        body_json["_pii_detected"] = True
                        body_json["_pii_types"] = pii_types

                        logger.warning(
                            "PII detected and redacted in request to %s: types=%s",
                            request.url.path,
                            pii_types,
                        )

                        # Create a new request with the redacted body
                        modified_body = json.dumps(body_json).encode("utf-8")

                        # Override the receive method to return the modified body
                        async def receive():
                            return {
                                "type": "http.request",
                                "body": modified_body,
                            }

                        request._receive = receive

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error("Failed to process request body for PII: %s", str(e))

        response = await call_next(request)
        return response
