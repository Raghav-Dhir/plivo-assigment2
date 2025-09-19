# Plivo Assignment 2 - FastAPI Pub/Sub Application

This repository contains a **FastAPI-based pub/sub application** with REST and WebSocket endpoints. The application allows clients to subscribe to topics, publish messages, and receive updates via WebSockets.

---

## Features

- **REST API endpoints** for managing topics and messages.
- **WebSocket endpoint** (`/ws`) for real-time pub/sub communication.
- **Configurable queue size and backpressure behavior** using environment variables.
- Fully **Dockerized** for easy deployment and development.

---

## Requirements

- Python 3.11+
- Docker / Colima (for running the app in containers)
- Dependencies listed in `requirements.txt`

---

## Docker Setup

The application can be run inside a Docker container. You can use **Colima** on macOS if you don’t have Docker Desktop.

### **1. Build the Docker Image**

```bash
docker build -t plivo-fastapi .
docker run --rm -p 8080:8080 -e QUEUE_SIZE=50 -e BACKPRESSURE=drop_oldest -v {path}/app plivo-fastapi