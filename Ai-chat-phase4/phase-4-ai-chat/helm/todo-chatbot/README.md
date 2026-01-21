# Todo Chatbot Helm Chart

A Helm chart for deploying the AI-powered Todo Chatbot on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+

## Parameters

### Backend Configuration

| Parameter                      | Description                                      | Default                         |
|-------------------------------|--------------------------------------------------|---------------------------------|
| `backend.image.repository`    | Backend image repository                         | `todo-chatbot-backend`          |
| `backend.image.tag`           | Backend image tag                                | `latest`                        |
| `backend.image.pullPolicy`    | Backend image pull policy                        | `IfNotPresent`                  |
| `backend.service.type`        | Backend service type                             | `ClusterIP`                     |
| `backend.service.port`        | Backend service port                             | `8000`                          |
| `backend.replicaCount`        | Number of backend replicas                       | `1`                             |
| `backend.env.DATABASE_URL`    | Database URL                                     | `sqlite+aiosqlite:////data/todo_chatbot.db` |
| `backend.env.APP_ENV`         | Application environment                          | `production`                    |
| `backend.env.LOG_LEVEL`       | Logging level                                    | `INFO`                          |

### Frontend Configuration

| Parameter                      | Description                                      | Default                         |
|-------------------------------|--------------------------------------------------|---------------------------------|
| `frontend.image.repository`   | Frontend image repository                        | `todo-chatbot-frontend`         |
| `frontend.image.tag`          | Frontend image tag                               | `latest`                        |
| `frontend.image.pullPolicy`   | Frontend image pull policy                       | `IfNotPresent`                  |
| `frontend.service.type`       | Frontend service type                            | `NodePort`                      |
| `frontend.service.port`       | Frontend service port                            | `80`                            |
| `frontend.service.nodePort`   | Frontend service node port (optional)            | `30080`                         |
| `frontend.replicaCount`       | Number of frontend replicas                      | `1`                             |

### Persistence

| Parameter                      | Description                                      | Default                         |
|-------------------------------|--------------------------------------------------|---------------------------------|
| `persistence.enabled`         | Enable persistence for SQLite database           | `true`                          |
| `persistence.storageClass`    | Storage class for persistent volume              | `""`                            |
| `persistence.accessMode`      | Access mode for persistent volume                | `ReadWriteOnce`                 |
| `persistence.size`            | Size of persistent volume                        | `1Gi`                           |

## Installation

To install the chart:

```bash
helm install todo-chatbot ./todo-chatbot
```

To install with custom values:

```bash
helm install todo-chatbot ./todo-chatbot -f values.yaml
```

## Uninstallation

To uninstall the chart:

```bash
helm uninstall todo-chatbot
```

## Upgrading

To upgrade the chart:

```bash
helm upgrade todo-chatbot ./todo-chatbot -f values.yaml
```