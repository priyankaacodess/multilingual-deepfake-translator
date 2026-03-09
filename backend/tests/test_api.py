import os
import time

os.environ["PIPELINE_MODE"] = "mock"

from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_languages() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/languages")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source_languages"]
    assert payload["target_languages"]


def test_create_job_and_poll() -> None:
    client = TestClient(app)
    files = {"video": ("demo.mp4", b"fake-video", "video/mp4")}
    data = {"source_language": "en", "target_language": "hi"}

    create_response = client.post("/api/v1/jobs", files=files, data=data)
    assert create_response.status_code == 200

    job_id = create_response.json()["job_id"]

    status = "queued"
    for _ in range(30):
        response = client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        payload = response.json()
        status = payload["status"]
        if status in {"completed", "failed"}:
            break
        time.sleep(0.1)

    assert status == "completed"
