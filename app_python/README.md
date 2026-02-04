# DevOps Info Service (FastAPI)

## Overview
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