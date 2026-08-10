"""Tests for SPA path traversal protection in backend/main.py."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient


class TestPathTraversal:
    """Verify the SPA catch-all route blocks path traversal attempts."""

    def _make_client(self, web_dir: Path):
        """Build a test app with a temp web_dir and a marker file outside it."""
        web_dir.mkdir(parents=True, exist_ok=True)
        (web_dir / "index.html").write_text("<html>TG-SignPulse</html>")

        # A secret file OUTSIDE web_dir that should never be served
        secret = Path(web_dir).parent / "secret.txt"
        secret.write_text("TOP-SECRET-DATA")

        # Save original APP_WEB_DIR and set our temp one
        self._saved_web_dir = os.environ.get("APP_WEB_DIR")
        os.environ["APP_WEB_DIR"] = str(web_dir)
        # Force re-import to pick up the env var
        import importlib

        import backend.main as main_mod

        importlib.reload(main_mod)
        return TestClient(main_mod.app), secret

    def _restore_env(self):
        """Restore the original APP_WEB_DIR and reload the module."""
        if hasattr(self, "_saved_web_dir"):
            if self._saved_web_dir is None:
                os.environ.pop("APP_WEB_DIR", None)
            else:
                os.environ["APP_WEB_DIR"] = self._saved_web_dir
        # Reload to restore original state
        import importlib

        import backend.main as main_mod

        importlib.reload(main_mod)

    def test_index_served(self):
        with tempfile.TemporaryDirectory() as d:
            web_dir = Path(d) / "web"
            client, _ = self._make_client(web_dir)
            with client:
                res = client.get("/")
                assert res.status_code == 200
                assert "TG-SignPulse" in res.text
        self._restore_env()

    def test_dot_dot_blocks_file_read(self):
        """`/../../secret.txt` must NOT serve the secret file.
        FastAPI/Starlette normalizes '..' segments before routing, so the
        path becomes `/secret.txt` which doesn't exist in web_dir. The SPA
        fallback serves index.html — the secret content must NOT leak.
        """
        with tempfile.TemporaryDirectory() as d:
            web_dir = Path(d) / "web"
            client, _ = self._make_client(web_dir)
            with client:
                res = client.get("/../../secret.txt")
                # Must NOT return the secret content
                assert "TOP-SECRET-DATA" not in res.text
                # SPA fallback serves index.html (normal behavior)
                assert "TG-SignPulse" in res.text
                assert res.status_code == 200
        self._restore_env()

    def test_double_encoding_blocks(self):
        """URL-encoded traversal should also be blocked."""
        with tempfile.TemporaryDirectory() as d:
            web_dir = Path(d) / "web"
            client, _ = self._make_client(web_dir)
            with client:
                res = client.get("/%2e%2e%2f%2e%2e%2fsecret.txt")
                assert "TOP-SECRET-DATA" not in res.text
                assert res.status_code in (400, 404)
        self._restore_env()

    def test_valid_nested_file_served(self):
        """A normal file inside web_dir should still be served."""
        with tempfile.TemporaryDirectory() as d:
            web_dir = Path(d) / "web"
            client, _ = self._make_client(web_dir)
            (web_dir / "hello.txt").write_text("hello")
            with client:
                res = client.get("/hello.txt")
                assert res.status_code == 200
                assert res.text == "hello"
        self._restore_env()
