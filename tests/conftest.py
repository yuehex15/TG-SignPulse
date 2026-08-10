from __future__ import annotations

import os
import tempfile
from pathlib import Path

# Configure isolated runtime env BEFORE backend modules are imported.
_TMP_ROOT = Path(tempfile.mkdtemp(prefix="tg-signpulse-pytest-"))
_DATA_DIR = _TMP_ROOT / "data"
_WEB_DIR = _TMP_ROOT / "web"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_WEB_DIR.mkdir(parents=True, exist_ok=True)
(_WEB_DIR / "index.html").write_text(
    "<!doctype html><title>TG-SignPulse</title>",
    encoding="utf-8",
)

os.environ["APP_DATA_DIR"] = str(_DATA_DIR)
os.environ["APP_WEB_DIR"] = str(_WEB_DIR)
os.environ["APP_SECRET_KEY"] = "test-secret-key-ci-only"
os.environ["ADMIN_PASSWORD"] = "AdminTest123!"
os.environ.setdefault("TZ", "Asia/Shanghai")
