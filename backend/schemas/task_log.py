from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

try:
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover - pydantic v1 compatibility
    ConfigDict = None

_PYDANTIC_V2 = hasattr(BaseModel, "model_validate")


class TaskLogOut(BaseModel):
    id: int
    task_id: int
    status: str
    log_path: str | None = None
    output: str | None = None
    started_at: datetime
    finished_at: datetime | None = None

    if _PYDANTIC_V2 and ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True
