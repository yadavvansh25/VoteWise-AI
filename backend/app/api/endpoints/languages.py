"""
VoteWise AI — Languages Endpoint
Returns supported languages.
"""

from fastapi import APIRouter
from app.models.schemas import LanguagesResponse, LanguageInfo

router = APIRouter()

SUPPORTED_LANGUAGES = [
    LanguageInfo(code="en", name="English", native_name="English"),
    LanguageInfo(code="hi", name="Hindi", native_name="हिन्दी"),
    LanguageInfo(code="ta", name="Tamil", native_name="தமிழ்"),
]


@router.get("/languages", response_model=LanguagesResponse)
async def get_languages() -> LanguagesResponse:
    """Return list of supported languages."""
    return LanguagesResponse(
        languages=SUPPORTED_LANGUAGES,
        default="en",
    )
