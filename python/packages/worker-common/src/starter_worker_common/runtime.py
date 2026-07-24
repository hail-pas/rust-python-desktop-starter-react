from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

PROTOCOL_VERSION = 1
Handler = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class WorkerInputError(ValueError):
    """An expected, user-correctable request validation error."""
