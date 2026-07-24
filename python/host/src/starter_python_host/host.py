from __future__ import annotations

import json
import os
import platform
import sys
import time
import traceback
from collections.abc import Mapping
from typing import Any

from starter_worker_common import PROTOCOL_VERSION, WorkerInputError

from .registry import WORKERS

HOST_NAME = "python-host"
HOST_STARTED_AT_UNIX_MS = int(time.time() * 1_000)
MAX_REQUEST_CHARACTERS = 65_536


def _metadata(worker: str) -> dict[str, Any]:
    return {
        "host": HOST_NAME,
        "hostPid": os.getpid(),
        "hostStartedAtUnixMs": HOST_STARTED_AT_UNIX_MS,
        "pythonVersion": platform.python_version(),
        "protocolVersion": PROTOCOL_VERSION,
        "worker": worker,
    }


def _response(
    *,
    request_id: str | None,
    worker: str,
    data: Mapping[str, Any] | None = None,
    code: str | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    ok = code is None
    return {
        "requestId": request_id,
        "ok": ok,
        "data": dict(data) if data is not None else None,
        "error": None if ok else {"code": code, "message": message},
        "meta": _metadata(worker),
    }


def process_message(message: object) -> dict[str, Any]:
    if not isinstance(message, dict):
        return _response(
            request_id=None,
            worker="unknown",
            code="INVALID_REQUEST",
            message="request must be a JSON object",
        )

    request_id = message.get("requestId")
    worker = message.get("worker")
    payload = message.get("payload")

    if not isinstance(request_id, str) or not request_id or len(request_id) > 128:
        return _response(
            request_id=request_id if isinstance(request_id, str) else None,
            worker=worker if isinstance(worker, str) else "unknown",
            code="INVALID_REQUEST_ID",
            message="requestId must be a non-empty string with at most 128 characters",
        )

    if not isinstance(worker, str):
        return _response(
            request_id=request_id,
            worker="unknown",
            code="INVALID_WORKER",
            message="worker must be a string",
        )

    handler = WORKERS.get(worker)
    if handler is None:
        return _response(
            request_id=request_id,
            worker=worker,
            code="UNKNOWN_WORKER",
            message=f"unknown logical worker: {worker}",
        )

    if not isinstance(payload, dict):
        return _response(
            request_id=request_id,
            worker=worker,
            code="INVALID_PAYLOAD",
            message="payload must be a JSON object",
        )

    try:
        data = handler(payload)
    except WorkerInputError as error:
        return _response(
            request_id=request_id,
            worker=worker,
            code="INVALID_INPUT",
            message=str(error),
        )
    except Exception as error:  # pragma: no cover - defensive host boundary
        traceback.print_exc(file=sys.stderr)
        return _response(
            request_id=request_id,
            worker=worker,
            code="INTERNAL_ERROR",
            message=str(error),
        )

    return _response(request_id=request_id, worker=worker, data=data)


def _write(response: Mapping[str, Any]) -> None:
    sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    sys.stdout.flush()


def run_forever() -> None:
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        if len(raw_line) > MAX_REQUEST_CHARACTERS:
            _write(
                _response(
                    request_id=None,
                    worker="unknown",
                    code="REQUEST_TOO_LARGE",
                    message="request is too large",
                )
            )
            continue

        try:
            message = json.loads(raw_line)
        except json.JSONDecodeError as error:
            _write(
                _response(
                    request_id=None,
                    worker="unknown",
                    code="INVALID_JSON",
                    message=str(error),
                )
            )
            continue

        _write(process_message(message))
