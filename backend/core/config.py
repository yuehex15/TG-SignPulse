from __future__ import annotations

import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Optional

from pydantic import BaseModel, Field

from backend.utils.storage import get_initial_data_dir, get_writable_base_dir, secure_write_text


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            if key:
                values[key] = value
    except OSError:
        return {}
    return values


def _merged_env() -> dict[str, str]:
    return {**_load_env_file(Path(".env")), **os.environ}


def _read_env(
    env: Mapping[str, str],
    *names: str,
    default: Optional[str] = None,
) -> Optional[str]:
    for name in names:
        value = str(env.get(name, "")).strip()
        if value:
            return value
    return default


def _read_int_env(env: Mapping[str, str], *names: str, default: int) -> int:
    raw = _read_env(env, *names)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _read_bool_env(env: Mapping[str, str], *names: str, default: bool) -> bool:
    raw = _read_env(env, *names)
    if raw is None:
        return default
    normalized_value = raw.strip().lower()
    if normalized_value in {"1", "true", "yes", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "off"}:
        return False
    return default


def _read_path_env(env: Mapping[str, str], *names: str) -> Optional[Path]:
    raw = _read_env(env, *names)
    if raw is None:
        return None
    return Path(raw).expanduser()


def get_default_secret_key(env: Optional[Mapping[str, str]] = None) -> str:
    env_map = env or os.environ
    env_secret = _read_env(env_map, "APP_SECRET_KEY")
    if env_secret:
        return env_secret

    data_dir = _read_path_env(env_map, "APP_DATA_DIR")
    base_dir = data_dir or get_initial_data_dir()
    if str(base_dir) == "/data":
        base_dir = get_writable_base_dir()
    base_dir.mkdir(parents=True, exist_ok=True)
    secret_file = base_dir / ".app_secret_key"

    try:
        existing = secret_file.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    except OSError:
        pass

    generated = secrets.token_urlsafe(48)
    try:
        secure_write_text(secret_file, generated)
    except OSError:
        pass
    return generated


_DEFAULT_CORS = (
    "http://127.0.0.1:8080,http://localhost:8080,"
    "http://127.0.0.1:5173,http://localhost:5173"
)


class Settings(BaseModel):
    app_name: str = "TG-SignPulse"
    host: str = "0.0.0.0"
    port: int = 8080
    cors_allow_origins_raw: str = _DEFAULT_CORS
    secret_key: str = Field(default_factory=get_default_secret_key)
    access_token_expire_hours: int = 12
    trust_proxy_headers: bool = False
    timezone: str = "Asia/Shanghai"
    data_dir: Path = Field(default_factory=get_initial_data_dir)
    db_path: Optional[Path] = None
    signer_workdir: Optional[Path] = None
    session_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None

    @classmethod
    def from_environment(cls) -> "Settings":
        env = _merged_env()
        return cls(
            app_name=_read_env(env, "APP_APP_NAME", "APP_NAME", default="TG-SignPulse"),
            host=_read_env(env, "APP_HOST", default="0.0.0.0"),
            port=_read_int_env(env, "APP_PORT", "PORT", default=8080),
            cors_allow_origins_raw=_read_env(
                env,
                "APP_CORS_ALLOW_ORIGINS",
                default=_DEFAULT_CORS,
            ),
            secret_key=get_default_secret_key(env),
            access_token_expire_hours=_read_int_env(
                env,
                "APP_ACCESS_TOKEN_EXPIRE_HOURS",
                default=12,
            ),
            trust_proxy_headers=_read_bool_env(
                env,
                "APP_TRUST_PROXY_HEADERS",
                default=False,
            ),
            timezone=_read_env(env, "TZ", "APP_TIMEZONE", default="Asia/Shanghai"),
            data_dir=_read_path_env(env, "APP_DATA_DIR") or get_initial_data_dir(),
            db_path=_read_path_env(env, "APP_DB_PATH"),
            signer_workdir=_read_path_env(env, "APP_SIGNER_WORKDIR"),
            session_dir=_read_path_env(env, "APP_SESSION_DIR"),
            logs_dir=_read_path_env(env, "APP_LOGS_DIR"),
        )

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.resolve_db_path()}?check_same_thread=False"

    def resolve_db_path(self) -> Path:
        return self.db_path or self.resolve_base_dir() / "db.sqlite"

    def resolve_workdir(self) -> Path:
        return self.signer_workdir or self.resolve_base_dir() / ".signer"

    def resolve_session_dir(self) -> Path:
        return self.session_dir or self.resolve_base_dir() / "sessions"

    def resolve_logs_dir(self) -> Path:
        return self.logs_dir or self.resolve_base_dir() / "logs"

    def resolve_base_dir(self) -> Path:
        if self.data_dir and str(self.data_dir) != "/data":
            return self.data_dir
        return get_writable_base_dir()

    @property
    def cors_allow_origins(self) -> list[str]:
        origins = [
            item.strip()
            for item in str(self.cors_allow_origins_raw or "").split(",")
            if item.strip()
        ]
        return origins or [
            "http://127.0.0.1:8080",
            "http://localhost:8080",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]


@lru_cache()
def get_settings() -> Settings:
    return Settings.from_environment()
