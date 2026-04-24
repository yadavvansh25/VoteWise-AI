"""
VoteWise AI — API Router
Aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.endpoints import chat, health, languages

api_router = APIRouter(prefix="/api")

api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(languages.router, tags=["Languages"])
