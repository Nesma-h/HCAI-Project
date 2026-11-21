"""Live synthetic-data checks against a locally running backend (3 Gemini API calls).
Run: python scripts/live_smoke.py [http://127.0.0.1:8000]
Never prints or needs the API key; reads it indirectly via the already running server.
"""
from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
TEXT = ("A synthetic study of 80 students found that practice reduced average "
        "reading time from 30 minutes to 20 minutes, but did not improve comprehension scores.")


def post(path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        f"{BASE}{path}",
        json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=90) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def verify(path: str, payload: dict, expected: int, key: str | None = None):
    status, body = post(path, payload)
    if status != expected:
        raise AssertionError(f"{path}: expected {expected}, got {status} ({body.get('detail', 'no detail')})")
    if key:
        if not isinstance(body.get(key), str) or not body[key].strip():
            raise AssertionError(f"{path}: missing nonempty {key}")
        if body.get("original_text") != TEXT:
            raise AssertionError(f"{path}: original text differs from input")
    print(f"PASS {path}: HTTP {status}" + (f", {key} present" if key else ""))


def main():
    try:
        verify("/simplify", {"text": TEXT, "user_action": True, "level": "base"}, 200, "simplified_text")
        verify("/summarize", {"text": TEXT, "user_action": True, "length": 2}, 200, "summary")
        verify("/explain", {"text": TEXT, "user_action": True, "term": "reading time", "style": "default"}, 200, "explanation")
        verify("/simplify", {"text": TEXT, "user_action": False}, 400)
        verify("/simplify", {"text": "   ", "user_action": True}, 400)
        verify("/explain", {"text": TEXT, "user_action": True, "term": "quantum entanglement"}, 400)
    except (URLError, AssertionError, ValueError, TimeoutError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print("Live API smoke checks passed. Review factual meaning of AI outputs separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
