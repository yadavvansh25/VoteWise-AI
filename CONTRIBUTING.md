# Contributing to VoteWise AI

## Development Setup
1. Clone the repository.
2. Install dependencies:
   - Backend: `pip install -r backend/requirements.txt`
   - Frontend: `npm install`
3. Set environment variables:
   - `GEMINI_API_KEY`
   - `GOOGLE_CLOUD_PROJECT` (for Secret Manager integration)

## Coding Standards
- **Python**: Follow PEP 8. Use type hints for all function signatures.
- **TypeScript**: Use strict mode. Prefer functional components.
- **CSS**: Use BEM naming convention for classes.

## Testing
- Run backend tests: `pytest --cov=app backend/tests/`
- Ensure 100% coverage for new features.

## Deployment
Pushing to the `main` branch triggers the GitHub Actions CI/CD pipeline which builds and validates the container.
