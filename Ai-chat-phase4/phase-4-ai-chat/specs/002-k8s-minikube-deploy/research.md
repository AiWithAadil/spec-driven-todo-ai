# Research: Kubernetes Minikube Deployment

## Analysis of Phase III Project Structure

### Backend (FastAPI Application)
- Located in `src/api/main.py` (likely entry point)
- Dependencies in `requirements.txt`
- Database connection via SQLite (based on spec)
- Likely uses uvicorn as ASGI server
- MCP server integration in `src/mcp_server.py`
- Database models in `src/models/`

### Frontend Location
- Based on spec: HTML/CSS/JS frontend exists
- Found in `frontend/` directory
- Served statically by FastAPI backend typically

### Database Configuration
- SQLite used for Phase IV (as specified)
- Connection logic in `src/db/connection.py`
- Models defined in `src/models/database.py`

## Docker Strategy

### Backend Container
- Base image: `python:3.11-slim` (minimal Python image)
- Install dependencies from `requirements.txt`
- Copy source code to container
- Expose port 8000
- Use uvicorn to run the FastAPI app
- Handle environment variables for configuration

### Frontend Container
- Base image: `nginx:alpine` (lightweight web server)
- Copy frontend files to nginx html directory
- Configure nginx to serve static files
- Set up reverse proxy for API calls if needed
- Expose port 80

## Existing Project Analysis

From examining the project structure:
- Backend: FastAPI application with OpenAI Agents SDK integration
- Frontend: ChatKit-based UI served from `/frontend` directory
- Database: Uses SQLModel with PostgreSQL in Phase III, but spec says SQLite for Phase IV
- Environment: Managed via `.env` file with environment variables

## Helm Chart Design

### Kubernetes Resources Needed
1. **Backend Deployment**: Runs FastAPI application
2. **Frontend Deployment**: Serves static assets via nginx
3. **Backend Service**: Internal service for API access
4. **Frontend Service**: External service for user access (NodePort)
5. **PersistentVolumeClaim**: For SQLite database persistence
6. **ConfigMap**: For application configuration
7. **Secret**: For sensitive data (API keys)

### Deployment Strategy
- Use Deployment controllers for both backend and frontend
- Set up proper resource limits and requests
- Configure health checks (liveness and readiness probes)
- Plan for graceful shutdowns
- Configure environment variables from ConfigMap/Secret

## Technology Decisions

### Decision: Use Multi-stage Docker builds
**Rationale**: To keep final images small and secure by separating build and runtime environments

### Decision: Use Init Containers for database initialization
**Rationale**: To ensure database schema is initialized before the main application starts

### Decision: Use ConfigMaps for non-sensitive configuration
**Rationale**: To keep configuration externalized and easily modifiable without rebuilding images

### Decision: Use NodePort for frontend service
**Rationale**: For simple local access without requiring LoadBalancer support in Minikube

## Alternatives Considered

### Alternative 1: Single container for both backend and frontend
- **Rejected**: Goes against microservices principles and makes scaling difficult
- **Impact**: Would tightly couple frontend and backend deployments

### Alternative 2: Use StatefulSet instead of Deployment for database
- **Rejected**: For SQLite with PV/PVC, Deployment is sufficient and simpler
- **Impact**: StatefulSet adds complexity without significant benefit for this use case

### Alternative 3: Use Ingress instead of NodePort
- **Rejected**: NodePort is simpler for local Minikube deployment
- **Impact**: Ingress requires additional configuration and may be overkill for local testing