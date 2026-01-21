# Quickstart: Kubernetes Minikube Deployment

## Overview

This guide walks through deploying the AI-powered Todo Chatbot to a local Minikube cluster using Helm charts. This deployment preserves all Phase III functionality while running the application in a Kubernetes environment.

## Prerequisites

- Docker Desktop or Docker Engine running
- Minikube installed and configured
- Helm 3.x installed
- kubectl installed

## Setup Instructions

### 1. Start Minikube

```bash
minikube start
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 3. Navigate to the Project Root

```bash
cd /mnt/c/Users/HP/Documents/Hackathon2/Ai-chat-phase3/phase-3-ai-chat
```

### 4. Build Docker Images

First, build the backend image:
```bash
cd docker
docker build -f Dockerfile.backend -t todo-chatbot-backend:latest .
```

Then, build the frontend image:
```bash
docker build -f Dockerfile.frontend -t todo-chatbot-frontend:latest .
```

### 5. Load Images into Minikube

```bash
minikube image load todo-chatbot-backend:latest
minikube image load todo-chatbot-frontend:latest
```

### 6. Deploy Using Helm

```bash
cd helm/todo-chatbot
helm install todo-chatbot . --values values.yaml
```

### 7. Verify Deployment

```bash
kubectl get pods
kubectl get services
```

### 8. Access the Application

Get the external URL:
```bash
minikube service todo-chatbot-frontend --url
```

## Configuration

### Environment Variables

The deployment uses the following environment variables:

- `DATABASE_URL`: SQLite database path (defaults to `/data/todo_chatbot.db`)
- `APP_ENV`: Application environment (defaults to `production`)
- `LOG_LEVEL`: Logging level (defaults to `INFO`)

### Persistent Storage

The SQLite database is stored in a PersistentVolumeClaim named `todo-chatbot-sqlite-pvc` to maintain data across pod restarts.

## Troubleshooting

### Common Issues

1. **Images not found**: Ensure you've loaded the images into minikube with `minikube image load`

2. **Service not accessible**: Check if minikube tunnel is running (on some platforms):
   ```bash
   minikube tunnel
   ```

3. **Pods stuck in Pending**: Check available resources in minikube:
   ```bash
   kubectl describe nodes
   ```

### Useful Commands

- Check pod logs: `kubectl logs -f deployment/todo-chatbot-backend`
- Port forward for debugging: `kubectl port-forward service/todo-chatbot-frontend 8080:80`
- Check resource usage: `kubectl top pods`

## Cleanup

To remove the deployment:
```bash
helm uninstall todo-chatbot
```

To stop minikube:
```bash
minikube stop
```