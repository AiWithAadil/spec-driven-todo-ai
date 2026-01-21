# Data Model: Kubernetes Minikube Deployment

## Overview

This data model describes the Kubernetes resources and configurations needed for deploying the existing Todo Chatbot application to Minikube. Since this is a deployment-focused feature, the underlying data models remain unchanged from Phase III, but we need to model the Kubernetes resources and configuration structures.

## Kubernetes Resource Models

### Backend Deployment Model
- **kind**: Deployment
- **apiVersion**: apps/v1
- **spec**:
  - replicas: 1 (for local deployment)
  - selector: Match labels for backend pods
  - template: Pod template with backend container
  - containers:
    - name: backend
    - image: todo-chatbot-backend:latest
    - ports: [{containerPort: 8000}]
    - envFrom: [{configMapRef: {name: backend-config}}]
    - volumeMounts: [{name: sqlite-storage, mountPath: /app/data}]
  - volumes: [{name: sqlite-storage, persistentVolumeClaim: {claimName: sqlite-pvc}}]

### Frontend Deployment Model
- **kind**: Deployment
- **apiVersion**: apps/v1
- **spec**:
  - replicas: 1 (for local deployment)
  - selector: Match labels for frontend pods
  - template: Pod template with frontend container
  - containers:
    - name: frontend
    - image: todo-chatbot-frontend:latest
    - ports: [{containerPort: 80}]
    - volumeMounts: [{name: nginx-config, mountPath: /etc/nginx/conf.d}]

### Services Model
- **Backend Service**:
  - kind: Service
  - apiVersion: v1
  - spec: ClusterIP type, exposing port 8000 internally
- **Frontend Service**:
  - kind: Service
  - apiVersion: v1
  - spec: NodePort type, exposing port 80 externally

### PersistentVolumeClaim Model
- **kind**: PersistentVolumeClaim
- **apiVersion**: v1
- **spec**:
  - accessModes: ["ReadWriteOnce"]
  - resources: requests storage 1Gi

### ConfigMap Model
- **kind**: ConfigMap
- **apiVersion**: v1
- **data**:
  - DATABASE_URL: "sqlite:///./todo_chatbot.db"
  - APP_ENV: "production"
  - LOG_LEVEL: "INFO"

## Deployment Configuration Model

### Environment Variables
- **DATABASE_URL**: SQLite database path in persistent storage
- **OPENAI_API_KEY**: API key for OpenAI integration (stored in Secret)
- **APP_ENV**: Environment designation (production for Kubernetes)
- **LOG_LEVEL**: Logging verbosity level

### Health Checks
- **Backend Liveness Probe**: HTTP GET /health endpoint
- **Backend Readiness Probe**: HTTP GET /ready endpoint
- **Timeouts**: 5 seconds initial delay, 10 seconds timeout, 5 seconds period

## Infrastructure Models

### Docker Image Specifications
- **Backend Image**:
  - Base: python:3.11-slim
  - Dependencies: From requirements.txt
  - Entrypoint: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
- **Frontend Image**:
  - Base: nginx:alpine
  - Assets: Static files from frontend/ directory
  - Configuration: Nginx config for serving static files

### Helm Values Model
- **image**: Container image tags and registries
- **resources**: CPU and memory limits/requests
- **service**: Service type and port configurations
- **persistence**: Storage size and class for database
- **env**: Environment variable mappings