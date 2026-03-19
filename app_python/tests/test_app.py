from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_root_structure():
    r = client.get("/", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    data = r.json()

    assert set(data.keys()) >= {"service", "system", "runtime", "request", "endpoints"}

    assert data["service"]["name"] == "devops-info-service"
    assert data["service"]["version"] == "1.0.0"
    assert data["service"]["framework"] == "FastAPI"
    
    for k in ["hostname", "platform", "platform_version", "architecture", "cpu_count", "python_version"]:
        assert k in data["system"]

    assert isinstance(data["runtime"]["uptime_seconds"], int)
    assert data["runtime"]["timezone"] == "UTC"

    assert data["request"]["method"] == "GET"
    assert data["request"]["path"] == "/"
    assert data["request"]["user_agent"] is not None

    paths = {e["path"] for e in data["endpoints"]}
    assert "/" in paths and "/health" in paths

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert isinstance(data["uptime_seconds"], int)
    assert "timestamp" in data

def test_404_json():
    r = client.get("/nope")
    assert r.status_code == 404
    data = r.json()
    assert data["error"] == "Not Found"


def test_metrics_endpoint():
    client.get("/")
    client.get("/health")

    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")

    body = r.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "http_requests_in_progress" in body
    assert "devops_info_endpoint_calls_total" in body
    assert 'endpoint="/"' in body
    assert 'endpoint="/health"' in body
