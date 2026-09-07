"""Exercise startup and the real SDK middleware without submitting payments."""

import base64
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RECIPIENT = "0x1111111111111111111111111111111111111111"
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", ["FACILITATOR_URL", "PAY_TO"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_startup_requires_explicit_configuration(name, value):
    env = {
        **os.environ,
        "FACILITATOR_URL": "http://127.0.0.1:1",
        "PAY_TO": RECIPIENT,
        "PYTHON_DOTENV_DISABLED": "1",
    }
    if value is None:
        env.pop(name, None)
    else:
        env[name] = value
    result = subprocess.run(
        [sys.executable, "-c", "import server"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1, result.stderr
    assert f"{name} is required" in result.stderr


def test_free_and_unpaid_routes_use_configured_recipient(monkeypatch):
    requests = []

    class FacilitatorHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.command, self.path))
            if self.path != "/supported":
                self.send_error(404)
                return
            body = json.dumps({
                "kinds": [{"x402Version": 2, "scheme": "exact", "network": "eip155:8453"}],
                "extensions": [],
                "signers": {},
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            requests.append((self.command, self.path))
            self.send_error(404)

        def log_message(self, format, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), FacilitatorHandler) as facilitator:
        worker = threading.Thread(target=facilitator.serve_forever, daemon=True)
        worker.start()
        try:
            monkeypatch.setenv("FACILITATOR_URL", f" http://127.0.0.1:{facilitator.server_port} ")
            monkeypatch.setenv("PAY_TO", f" {RECIPIENT} ")
            monkeypatch.setenv("PRICE", "$0.001")
            monkeypatch.setenv("NETWORK", "eip155:8453")
            monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
            from server import app

            with TestClient(app) as client:
                hello = client.get("/api/hello")
                assert hello.status_code == 200
                assert hello.json() == {"message": "Hello from x402!"}

                premium = client.get("/api/premium", headers={"Accept": "application/json"})
                assert premium.status_code == 402, premium.text
                requirements = json.loads(base64.b64decode(premium.headers["PAYMENT-REQUIRED"]))
                assert requirements["x402Version"] == 2
                option = requirements["accepts"][0]
                assert option["payTo"] == RECIPIENT
                assert option["network"] == "eip155:8453"
                assert option["amount"] == "1000"
                assert option["scheme"] == "exact"
                assert "The answer is 42" not in premium.text
            assert requests
            assert all(request == ("GET", "/supported") for request in requests)
        finally:
            facilitator.shutdown()
            worker.join(timeout=5)
