# Deployment Guide: AI-Powered Todo Chatbot

This document describes how to deploy the AI-powered Todo Chatbot application using Kubernetes and Helm.

## Overview

The Todo Chatbot application is designed to be deployed on Kubernetes using Helm charts. The application consists of two main components:

1. **Backend**: A FastAPI application that handles the AI-powered todo management logic
2. **Frontend**: A static web interface that communicates with the backend

## Prerequisites

- Kubernetes cluster (tested with Minikube)
- Helm 3.x
- Docker (for building images)

## Deployment Steps

### 1. Prepare Docker Images

First, build the Docker images for both backend and frontend:

```bash
# Build backend image
docker build -f docker/Dockerfile.backend -t todo-chatbot-backend:latest .

# Build frontend image
docker build -f docker/Dockerfile.frontend -t todo-chatbot-frontend:latest .
```

If using Minikube, load the images into the cluster:

```bash
minikube image load todo-chatbot-backend:latest
minikube image load todo-chatbot-frontend:latest
```

### 2. Deploy with Helm

Navigate to the Helm chart directory and install:

```bash
cd helm/todo-chatbot

# Install the chart
helm install todo-chatbot . --values values.yaml

# Or install with custom values
helm install todo-chatbot . --set backend.image.tag=latest --set frontend.image.tag=latest
```

### 3. Verify Deployment

Check that all pods are running:

```bash
kubectl get pods
```

Check the services:

```bash
kubectl get services
```

### 4. Access the Application

If deployed with NodePort service type, find the NodePort:

```bash
kubectl get services todo-chatbot-frontend-service
```

Then access the application at `http://<minikube-ip>:<nodeport>`

For Minikube, you can get the URL directly:

```bash
minikube service todo-chatbot-frontend-service --url
```

## Configuration

The application can be configured using the values.yaml file or by setting individual values during installation.

### Backend Configuration

- `backend.image.repository`: Backend Docker image repository
- `backend.image.tag`: Backend Docker image tag
- `backend.replicaCount`: Number of backend replicas
- `backend.env.DATABASE_URL`: Database connection string
- `backend.env.OPENAI_API_KEY`: OpenAI API key (optional, can be provided via secret)

### Frontend Configuration

- `frontend.image.repository`: Frontend Docker image repository
- `frontend.image.tag`: Frontend Docker image tag
- `frontend.replicaCount`: Number of frontend replicas
- `frontend.service.type`: Service type (ClusterIP, NodePort, LoadBalancer)
- `frontend.service.nodePort`: Specific NodePort to use (optional)

### Persistence

The application uses a PersistentVolumeClaim for SQLite database storage to maintain data across pod restarts:

- `persistence.enabled`: Enable/disable persistence (default: true)
- `persistence.size`: Size of the persistent volume (default: 1Gi)
- `persistence.storageClass`: Storage class to use (default: "")

## Upgrading

To upgrade the application:

```bash
# Update the chart
helm upgrade todo-chatbot . --values values.yaml
```

## Uninstalling

To remove the application:

```bash
helm uninstall todo-chatbot
```

## Troubleshooting

### Pods not starting

Check the pod status and logs:

```bash
kubectl get pods
kubectl logs -l app=backend
kubectl logs -l app=frontend
```

### Service not accessible

Verify the service configuration:

```bash
kubectl get services
kubectl describe service todo-chatbot-frontend-service
```

### Database connectivity issues

Check that the PVC is bound and accessible:

```bash
kubectl get pvc
kubectl describe pvc todo-chatbot-sqlite-pvc
```