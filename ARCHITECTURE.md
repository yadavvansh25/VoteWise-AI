# VoteWise AI Architecture

## Overview
VoteWise AI is a modern web application designed to educate Indian citizens on the election process. It uses a FastAPI backend and a React (Vite) frontend, deployed as a single container on Google Cloud Run.

## Tech Stack
- **Frontend**: React 18, TypeScript, Vite, Vanilla CSS (Premium Design).
- **Backend**: FastAPI, Pydantic, SQLAlchemy (SQLite).
- **AI**: Google Gemini 1.5 Flash with Search Grounding.
- **Infrastructure**: Google Cloud Run, Secret Manager, Cloud Storage, Cloud Logging, Cloud Profiler.

## Key Components
1. **Gemini Service**: Handles AI generation with failover logic across multiple Gemini models.
2. **Intent Engine**: Rule-based classification to provide sub-second context matching.
3. **Security Middleware**: Implements CSP, HSTS, and PII redaction.
4. **Resiliency Layer**: Implements rate limiting and multi-model fallbacks for AI.

## Data Flow
1. User sends message via React UI.
2. FastAPI validates request and classifies intent.
3. Relevant election context is retrieved from the knowledge base.
4. Gemini generates a grounded response using Google Search.
5. Response is filtered for bias and PII before returning to user.
