# Phase 4: Cloud Native Todo Chatbot Deployment

## Project Overview
This project demonstrates the deployment of a cloud-native Todo Chatbot application using Kubernetes, Helm, and Docker containerization. The application was originally developed in Phase 3 and is now deployed on a local Kubernetes cluster using Minikube.

## Architecture
- **Frontend**: Static web interface served by nginx
- **Backend**: FastAPI application with AI-powered todo management
- **Database**: SQLite with persistent storage
- **Orchestration**: Kubernetes on Minikube
- **Packaging**: Helm charts for deployment

## Phase 4 Requirements Fulfilled

✅ **Containerization**: Docker images for both frontend and backend
✅ **Helm Charts**: Complete Helm chart for deployment management
✅ **Kubernetes Deployment**: Running on local Minikube cluster
✅ **Docker AI (Gordon)**: Used for intelligent Docker operations
✅ **kubectl-ai/kagent**: Used for AI-assisted Kubernetes operations
✅ **Local Deployment**: Minikube-based local Kubernetes cluster
✅ **Working Application**: Fully functional Todo Chatbot
✅ **Phase III Code Preservation**: No changes to application logic

## Deployment Structure

```
├── docker/                     # Docker configuration
│   ├── Dockerfile.backend      # Backend container
│   ├── Dockerfile.frontend     # Frontend container
│   └── nginx.conf             # Nginx configuration
├── helm/todo-chatbot/         # Helm chart
│   ├── Chart.yaml             # Chart metadata
│   ├── values.yaml            # Default values
│   ├── templates/             # Kubernetes templates
│   └── README.md              # Chart documentation
├── frontend/                  # Frontend source code
├── src/                       # Backend source code
├── docs/                      # Documentation
└── docker-compose.yml         # Local development config
```

## Deployment Commands

1. **Start Minikube**:
   ```bash
   minikube start
   ```

2. **Deploy with Helm**:
   ```bash
   helm install todo-chatbot ./helm/todo-chatbot
   ```

3. **Access Application**:
   ```bash
   minikube service todo-chatbot-frontend-service --url
   ```

4. **Verify Deployment**:
   ```bash
   kubectl get pods
   kubectl get services
   helm list
   ```

## Key Features

- **AI-Powered Todo Management**: Natural language processing for todo operations
- **Persistent Storage**: SQLite database with PVC for data persistence
- **Service Discovery**: Proper Kubernetes service communication
- **Health Checks**: Liveness and readiness probes
- **Reverse Proxy**: Nginx handles API routing between frontend and backend
- **Scalability**: Configurable replica counts

## Technologies Used

- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube)
- **Package Management**: Helm
- **AI Operations**: Docker AI (Gordon), kubectl-ai, Kagent
- **Backend**: FastAPI, Python
- **Frontend**: HTML/CSS/JS with nginx
- **Database**: SQLite with persistent volumes

## Verification

After deployment:
- Both pods show `Running` status
- Frontend is accessible via NodePort
- Backend API is reachable through nginx proxy
- Chat functionality works end-to-end
- Data persists across pod restarts

## Project Status

**COMPLETED**: All Phase 4 requirements successfully implemented and verified.