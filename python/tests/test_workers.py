import pytest
from starter_python_host.host import process_message
from starter_worker_common import WorkerInputError
from starter_worker_greeter.handler import handle as greet
from starter_worker_statistics.handler import handle as statistics


def test_greeter_normalizes_whitespace() -> None:
    result = greet({"name": "  Ada   Lovelace  "})
    assert result["normalizedName"] == "Ada Lovelace"


def test_greeter_rejects_empty_name() -> None:
    with pytest.raises(WorkerInputError):
        greet({"name": "   "})


def test_statistics() -> None:
    result = statistics({"values": [1, 2, 3, 4, 5]})
    assert result == {
        "count": 5,
        "sum": 15.0,
        "mean": 3.0,
        "minimum": 1.0,
        "maximum": 5.0,
    }


def test_statistics_rejects_boolean() -> None:
    with pytest.raises(WorkerInputError):
        statistics({"values": [True]})


def test_logical_workers_share_one_host_runtime() -> None:
    greeting = process_message(
        {"requestId": "test-1", "worker": "greeter", "payload": {"name": "Ada"}}
    )
    stats = process_message(
        {
            "requestId": "test-2",
            "worker": "statistics",
            "payload": {"values": [1, 2, 3]},
        }
    )
    assert greeting["ok"] is True
    assert stats["ok"] is True
    assert greeting["meta"]["hostPid"] == stats["meta"]["hostPid"]
    assert greeting["meta"]["hostStartedAtUnixMs"] == stats["meta"]["hostStartedAtUnixMs"]
