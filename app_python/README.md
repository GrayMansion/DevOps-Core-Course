# DevOps Info Service (FastAPI)

## Overview

[![python-ci](https://github.com/GrayMansion/DevOps-Core-Course/actions/workflows/python-ci.yml/badge.svg)](https://github.com/GrayMansion/DevOps-Core-Course/actions/workflows/python-ci.yml)

A small web service that exposes system/runtime information and a health check endpoint.

## Prerequisites
- Python 3.11+
- pip

## Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application
```bash
python app.py
```

## Custom config:
```bash
PORT=8080 python app.py
HOST=127.0.0.1 PORT=3000 python app.py
DEBUG=true python app.py
```

## API Endpoints
```bash
GET / — Service and system information
GET /health — Health check
```

## Configuration
| Variable | Default | Meaning                                 |
| -------- | ------- | --------------------------------------- |
| HOST     | 0.0.0.0 | Bind address                            |
| PORT     | 5000    | Listening port                          |
| DEBUG    | False   | If true, enables reload + debug logging |

## Docker

This project can be built and run as a Docker container (same API behavior as local run).

### Build the image
```bash
docker build -t <image_name>:<tag> -f app_python/Dockerfile app_python
```

### Run the container
The app listens on container port `<container_port>` (default is `5000`), so you publish it to a host port:

```bash
docker run --rm -p <host_port>:<container_port> <image_name>:<tag>
```

### Pull from Docker Hub
```bash
docker pull graymansion/devops-info-service:lab02
docker run --rm -p <host_port>:<container_port> graymansion/devops-info-service:lab02
```

