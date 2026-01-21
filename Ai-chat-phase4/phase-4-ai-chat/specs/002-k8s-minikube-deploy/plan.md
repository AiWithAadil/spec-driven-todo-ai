# Implementation Plan: Kubernetes Minikube Deployment

**Branch**: `002-k8s-minikube-deploy` | **Date**: 2026-01-17 | **Spec**: [link]

**Input**: Feature specification from `/specs/002-k8s-minikube-deploy/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy the existing Phase III AI-powered Todo Chatbot application to a local Kubernetes cluster using Minikube. This involves containerizing the FastAPI backend and HTML/CSS/JS frontend without modifying the application code, creating Helm charts for deployment management, and ensuring all functionality remains intact after deployment.

## Technical Context

**Language/Version**: Python 3.11 (for FastAPI backend), JavaScript (for frontend)
**Primary Dependencies**: FastAPI, Docker, Kubernetes, Helm, Minikube
**Storage**: SQLite (as established in Phase III)
**Testing**: N/A (deployment-focused feature)
**Target Platform**: Linux/Windows/Mac local Minikube cluster
**Project Type**: Web application (existing)
**Performance Goals**: Maintain existing response times (< 3 seconds)
**Constraints**: Phase III code remains unchanged; only Docker, Helm, and Kubernetes files added
**Scale/Scope**: Single local cluster deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Verify Phase III code remains unchanged during Phase IV
- Confirm only Docker, Helm, and Kubernetes-related files are added
- Ensure deployment aligns with container orchestration standards
- Validate use of AI-assisted tools (Docker AI, kubectl-ai, kagent) when available
- Confirm local Minikube deployment approach
- Verify minimal and explainable deployment configuration

## Project Structure

### Documentation (this feature)
```text
specs/002-k8s-minikube-deploy/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
src/
├── api/                 # FastAPI application (Phase III - READ-ONLY)
├── services/            # Business logic (Phase III - READ-ONLY)
├── models/              # Database and Pydantic schemas (Phase III - READ-ONLY)
├── db/                  # Database connection and migrations (Phase III - READ-ONLY)
└── utils/               # Utilities (Phase III - READ-ONLY)
├── docker/              # New Docker-related files
├── helm/                # New Helm chart files
└── k8s/                 # New Kubernetes manifest files (if needed)
```

**Structure Decision**: Add new deployment infrastructure alongside existing Phase III code without modification. New directories will contain Dockerfiles, Helm charts, and Kubernetes configurations.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None identified] | [N/A] | [N/A] |

## Phase 0: Research & Analysis

### Research Tasks

1. **Analyze Phase III project structure**:
   - Identify backend (FastAPI) entry point and dependencies
   - Identify frontend (HTML/CSS/JS) structure and static assets
   - Locate database configuration and SQLite setup
   - Document existing environment variables and configuration

2. **Determine Docker strategy**:
   - Research optimal Dockerfile for FastAPI backend
   - Research optimal Dockerfile for HTML/CSS/JS frontend
   - Identify necessary environment variables and secrets handling
   - Plan volume mounts for SQLite database persistence

3. **Design Helm chart structure**:
   - Research standard Helm chart patterns for web applications
   - Plan deployment structure for backend and frontend
   - Design service configurations (NodePort vs LoadBalancer)
   - Plan persistent volume claims for SQLite database

### Expected Research Outcomes

- Clear understanding of Phase III application structure
- Dockerfile templates for both backend and frontend
- Helm chart structure with all necessary Kubernetes resources
- Configuration mapping for environment variables and secrets

## Phase 1: Design & Architecture

### Backend Container Design

- **Image**: Python-based container with FastAPI application
- **Dependencies**: All requirements from requirements.txt
- **Entry point**: uvicorn server for FastAPI application
- **Ports**: Expose port 8000 (standard FastAPI port)
- **Health checks**: Liveness and readiness probes to /health endpoint
- **Environment**: Support for DATABASE_URL and other required env vars

### Frontend Container Design

- **Image**: Nginx-based container serving static HTML/CSS/JS files
- **Assets**: All frontend files copied to appropriate nginx directory
- **Ports**: Expose port 80 (standard HTTP)
- **Configuration**: Nginx configuration to serve static assets and handle API proxying

### Kubernetes Resources Design

- **Backend Deployment**: Deployment for FastAPI application
- **Frontend Deployment**: Deployment for static file server
- **Backend Service**: Service to expose backend within cluster
- **Frontend Service**: Service to expose frontend externally (NodePort)
- **PersistentVolumeClaim**: Storage for SQLite database persistence
- **ConfigMap**: Application configuration
- **Secrets**: Sensitive configuration (API keys, etc.)

### Helm Chart Structure

```text
helm/todo-chatbot/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-service.yaml
│   ├── pvc.yaml
│   ├── configmap.yaml
│   └── secret.yaml
└── README.md
```

### Data Model Considerations

Since this is a deployment-focused feature, the data model remains unchanged from Phase III. The existing Todo, Message, and Conversation models will continue to be used with SQLite database persistence managed through Kubernetes PVC.

## Phase 2: Implementation Approach

### Prerequisites

1. Minikube installed and running locally
2. Helm installed
3. Docker daemon running
4. Access to existing Phase III codebase

### Implementation Steps

1. **Containerization Phase**:
   - Create Dockerfile for FastAPI backend
   - Create Dockerfile for frontend static server
   - Build and test containers locally
   - Verify functionality matches Phase III behavior

2. **Helm Chart Creation Phase**:
   - Create Helm chart structure
   - Implement Kubernetes resource templates
   - Test Helm chart installation locally
   - Verify deployment, service, and persistence functionality

3. **Integration Phase**:
   - Connect backend and frontend services
   - Configure database persistence
   - Test complete application functionality
   - Validate all Todo Chatbot features work as expected

### Success Criteria Verification

- Application deploys successfully on Minikube within 5 minutes
- All existing Todo Chatbot functionality remains available and responsive
- Application maintains data persistence across pod restarts
- System achieves high availability during local testing
- Deployment can be rolled back to a previous version within 2 minutes