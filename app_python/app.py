"""
DevOps Info Service (Lab 1)
FastAPI implementation.
"""

import logging
import os
import platform
import socket
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# -------------------------
# Configuration (env vars)
# -------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("devops-info-service")

# -------------------------
# App + runtime state
# -------------------------
app = FastAPI(title="DevOps Info Service", version="1.0.0")
START_TIME = datetime.now(timezone.utc)


def iso_utc_now() -> str:
    # Example desired format: 2026-01-07T14:30:00.000Z
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def get_uptime() -> dict:
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return {"seconds": seconds, "human": f"{hours} hours, {minutes} minutes"}


def get_platform_version() -> str:
    # Try to get something user-friendly on Linux (e.g., "Ubuntu 24.04").
    if hasattr(platform, "freedesktop_os_release"):
        try:
            data = platform.freedesktop_os_release()
            pretty = data.get("PRETTY_NAME")
            if pretty:
                return pretty
        except Exception:
            pass
    # Fallback for other OSes.
    return platform.platform()


def get_system_info() -> dict:
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": get_platform_version(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count() or 1,
        "python_version": platform.python_version(),
    }


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "message": "Endpoint does not exist"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "message": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "An unexpected error occurred"},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Request: %s %s", request.method, request.url.path)
    return await call_next(request)


@app.get("/")
async def index(request: Request) -> dict:
    uptime = get_uptime()

    return {
        "service": {
            "name": "devops-info-service",
            "version": "1.0.0",
            "description": "DevOps course info service",
            "framework": "FastAPI",
        },
        "system": get_system_info(),
        "runtime": {
            "uptime_seconds": uptime["seconds"],
            "uptime_human": uptime["human"],
            "current_time": iso_utc_now(),
            "timezone": "UTC",
        },
        "request": {
            "client_ip": (request.client.host if request.client else None),
            "user_agent": request.headers.get("user-agent"),
            "method": request.method,
            "path": request.url.path,
        },
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
        ],
    }


@app.get("/health")
async def health() -> dict:
    uptime = get_uptime()
    return {
        "status": "healthy",
        "timestamp": iso_utc_now(),
        "uptime_seconds": uptime["seconds"],
    }


if __name__ == "__main__":
    logger.info("Starting app on %s:%s (debug=%s)", HOST, PORT, DEBUG)
    uvicorn.run("app:app", host=HOST, port=PORT, reload=DEBUG)