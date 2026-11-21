"""HTTP-level tests using FastAPI's TestClient (needs `httpx`:
pip install -r requirements-dev.txt). The model is mocked."""

import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)
TEXT = "Working memory has a limited capacity."


@pytest.fixture
def fake_model(monkeypatch):
    prompts = []
    monkeypatch.setattr(
        main, "generate_with_gemini", lambda prompt: prompts.append(prompt) or "ok"
    )
    return prompts


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"]


@pytest.mark.parametrize(
    "path,key",
    [("/simplify", "simplified_text"), ("/summarize", "summary"), ("/explain", "explanation")],
)
def test_endpoints_return_ui_compatible_json(fake_model, path, key):
    response = client.post(path, json={"text": TEXT, "user_action": True})
    assert response.status_code == 200
    body = response.json()
    assert body["original_text"] == TEXT
    assert body[key] == "ok"


def test_user_action_false_is_400_and_model_not_called(fake_model):
    response = client.post("/simplify", json={"text": TEXT, "user_action": False})
    assert response.status_code == 400
    assert fake_model == []


def test_validation_error_is_a_readable_string_without_echoing_text(fake_model):
    response = client.post("/simplify", json={"text": TEXT})  # user_action missing
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str) and "user_action" in detail
    assert TEXT not in detail
    assert fake_model == []


def test_missing_api_key_is_503(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/summarize", json={"text": TEXT, "user_action": True})
    assert response.status_code == 503


def test_openapi_documents_errors_and_response_models():
    specification = client.get("/openapi.json").json()
    for path in ("/simplify", "/summarize", "/explain"):
        responses = specification["paths"][path]["post"]["responses"]
        for status in ("200", "400", "422", "502", "503", "504"):
            assert status in responses
        assert "schema" in responses["200"]["content"]["application/json"]
