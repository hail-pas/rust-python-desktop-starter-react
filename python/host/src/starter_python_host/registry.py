from __future__ import annotations

from starter_worker_common import Handler
from starter_worker_greeter.handler import handle as handle_greeter
from starter_worker_statistics.handler import handle as handle_statistics

WORKERS: dict[str, Handler] = {
    "greeter": handle_greeter,
    "statistics": handle_statistics,
}
