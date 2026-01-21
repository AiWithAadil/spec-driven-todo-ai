# Docker Configuration for Todo Chatbot

This directory contains the Docker configuration files for the AI-powered Todo Chatbot application.

## Overview

The application is containerized into two separate services:

1. **Backend**: FastAPI application that handles the AI-powered todo management
2. **Frontend**: Static web interface served by nginx

## Docker Files

### Backend (`Dockerfile.backend`)

The backend Dockerfile creates an image for the FastAPI application:

- Uses Python 3.11 slim image as base
- Installs dependencies from requirements.txt
- Copies the application code
- Exposes port 8000
- Runs the application with uvicorn

### Frontend (`Dockerfile.frontend`)

The frontend Dockerfile creates an image with nginx to serve static files:

- Uses nginx:alpine as base image
- Copies custom nginx configuration
- Copies frontend files to nginx html directory
- Exposes port 80
- Starts nginx server

### Nginx Configuration (`nginx.conf`)

The nginx configuration includes:

- Static file serving for the frontend
- API request proxying to the backend service
- Health check endpoint

## Building Images

To build the Docker images:

```bash
# Build backend image
docker build -f Dockerfile.backend -t todo-chatbot-backend:latest .

# Build frontend image
docker build -f Dockerfile.frontend -t todo-chatbot-frontend:latest .
```

## Local Testing

Use the docker-compose file for local testing:

```bash
docker-compose up --build
```

This will start both the backend and frontend services and connect them appropriately.

## Environment Variables

The backend service supports the following environment variables:

- `DATABASE_URL`: Database connection string (default: sqlite+aiosqlite:///./todo_chatbot.db)
- `OPENAI_API_KEY`: OpenAI API key for AI functionality
- `APP_ENV`: Application environment (development, production)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Health Checks

The backend includes health check endpoints:
- `/health`: Basic health check
- `/ready`: Readiness check

The frontend includes a basic health check at `/health`.

## Best Practices

- Use multi-stage builds to reduce image size
- Install only necessary dependencies
- Use non-root user for running the application (when possible)
- Properly configure health checks
- Set appropriate resource limits
- Use .dockerignore to exclude unnecessary files