"""Tests for config import path traversal protection."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from backend.services.config import ConfigService


def _make_service() -> tuple[ConfigService, Path]:
    svc = ConfigService.__new__(ConfigService)
    tmp = Path(tempfile.mkdtemp(prefix="tg-config-test-"))
    svc.workdir = tmp
    svc.monitors_dir = tmp / "monitors"
    svc.signs_dir = tmp / "signs"
    svc.monitors_dir.mkdir()
    return svc, tmp


class TestConfigImportPathTraversal:
    def test_monitor_task_traversal_blocked(self):
        """A monitor task name with '..' must not write outside monitors_dir."""
        svc, tmp = _make_service()
        malicious = {"monitors": {"../evil": {"x": 1}}}
        result = svc.import_all_configs(json.dumps(malicious), overwrite=True)

        assert tmp / "evil" / "config.json" not in (
            f for f in tmp.rglob("*.json")
        )
        assert result["monitors_imported"] == 0
        assert any("Invalid monitor task name" in e for e in result["errors"])

    def test_monitor_task_separator_blocked(self):
        """A monitor task name with '/' must be rejected."""
        svc, _ = _make_service()
        malicious = {"monitors": {"a/b": {"x": 1}}}
        result = svc.import_all_configs(json.dumps(malicious), overwrite=True)
        assert result["monitors_imported"] == 0
        assert any("Invalid monitor task name" in e for e in result["errors"])

    def test_valid_monitor_task_imports(self):
        """A valid monitor task name should import successfully."""
        svc, _ = _make_service()
        valid = {"monitors": {"my_monitor": {"keywords": ["a"], "action": {}}}}
        result = svc.import_all_configs(json.dumps(valid), overwrite=True)
        assert result["monitors_imported"] == 1
        assert (svc.monitors_dir / "my_monitor" / "config.json").exists()

    def test_sign_task_traversal_blocked(self):
        """Sign task 'name' field with path separator must be rejected."""
        svc, tmp = _make_service()
        malicious = {
            "signs": {
                "task1": {"name": "../evil_sign", "account_name": "acc1", "chats": []}
            }
        }
        result = svc.import_all_configs(json.dumps(malicious), overwrite=True)
        assert not (tmp / "evil_sign").exists()
        assert result["signs_imported"] == 0