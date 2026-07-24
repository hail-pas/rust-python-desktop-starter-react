from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from starter_worker_common import WorkerInputError


def handle(request: Mapping[str, Any]) -> Mapping[str, Any]:
    raw_values = request.get("values")
    if not isinstance(raw_values, list):
        raise WorkerInputError("values must be an array")
    if len(raw_values) > 1_000:
        raise WorkerInputError("values contains too many items")

    values: list[float] = []
    for index, raw_value in enumerate(raw_values):
        if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
            raise WorkerInputError(f"values[{index}] must be a number")
        value = float(raw_value)
        if not math.isfinite(value):
            raise WorkerInputError(f"values[{index}] must be finite")
        values.append(value)

    total = math.fsum(values)
    return {
        "count": len(values),
        "sum": total,
        "mean": total / len(values) if values else None,
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
    }
