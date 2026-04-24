"""
VoteWise AI — Pydantic Schemas
Request/Response models for the API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"


class Intent(str, Enum):
    """Conversation intent categories."""
    REGISTRATION = "registration"
    CANDIDATE_INFO = "candidate_info"
    PROCESS_EDUCATION = "process_education"
    GENERAL = "general"
    GREETING = "greeting"


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content text")
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Incoming chat request."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message text"
    )
    language: Language = Field(
        default=Language.ENGLISH,
        description="Response language preference"
    )
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation messages for context"
    )


class SourceCitation(BaseModel):
    """A grounding source citation."""
    title: str = Field(..., description="Source page title")
    url: str = Field(..., description="Source URL")
    snippet: Optional[str] = Field(None, description="Relevant text snippet")


class PIIDetectionInfo(BaseModel):
    """Information about detected PII."""
    detected: bool = Field(default=False, description="Whether PII was detected")
    types: List[str] = Field(default_factory=list, description="Types of PII found")
    message: Optional[str] = Field(
        None,
        description="User-facing message about PII redaction"
    )


class ChatResponse(BaseModel):
    """Outgoing chat response."""
    message: str = Field(..., description="Assistant's response text")
    intent: Intent = Field(
        default=Intent.GENERAL,
        description="Detected conversation intent"
    )
    language: Language = Field(
        default=Language.ENGLISH,
        description="Response language"
    )
    sources: List[SourceCitation] = Field(
        default_factory=list,
        description="Google Search Grounding sources"
    )
    pii_info: PIIDetectionInfo = Field(
        default_factory=PIIDetectionInfo,
        description="PII detection details"
    )
    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Response timestamp"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict = Field(default_factory=dict)


class LanguageInfo(BaseModel):
    """Language information."""
    code: str
    name: str
    native_name: str


class LanguagesResponse(BaseModel):
    """Available languages response."""
    languages: List[LanguageInfo]
    default: str = "en"
