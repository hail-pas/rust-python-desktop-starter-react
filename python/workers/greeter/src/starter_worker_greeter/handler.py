from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from starter_worker_common import WorkerInputError


def handle(request: Mapping[str, Any]) -> Mapping[str, Any]:
    raw_name = request.get("name")
    if not isinstance(raw_name, str):
        raise WorkerInputError("name must be a string")

    normalized_name = " ".join(raw_name.split())
    if not normalized_name:
        raise WorkerInputError("name must not be empty")
    if len(normalized_name) > 100:
        raise WorkerInputError("name is too long")

    return {
        "greeting": (
            f"你好，{normalized_name}！"
            "这条消息来自常驻 Python Host 中的 greeter 逻辑 Worker。"
        ),
        "normalizedName": normalized_name,
    }
