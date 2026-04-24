# --- Stage 1: Build Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python Backend ---
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend build artifacts to backend/static
COPY --from=frontend-builder /app/frontend/dist ./static

# Create non-root user for security
RUN adduser --disabled-password --gecos "" votewise
RUN chown -R votewise:votewise /app
USER votewise

# Environment variables
ENV PORT=8080
ENV DATABASE_PATH=/app/votewise.db

# Expose port and run
EXPOSE 8080
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080"]
