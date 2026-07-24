from __future__ import annotations

import json
import subprocess
import sys

from worker_manifest import discover_host, discover_workers


def build_input() -> tuple[str, list[str]]:
    request_ids: list[str] = []
    lines: list[str] = []
    for index, worker in enumerate(discover_workers(), start=1):
        request_id = f"source-smoke-{index}"
        request_ids.append(request_id)
        lines.append(
            json.dumps(
                {
                    "requestId": request_id,
                    "worker": worker.name,
                    "payload": json.loads(worker.sample_request),
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + "\n", request_ids


def main() -> None:
    host = discover_host()
    stdin, request_ids = build_input()
    result = subprocess.run(
        [sys.executable, "-m", host.module],
        input=stdin,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Python Host source smoke test failed: {result.stderr.strip()}")

    responses = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    if len(responses) != len(request_ids):
        raise RuntimeError(f"expected {len(request_ids)} responses, received {len(responses)}")
    if [item.get("requestId") for item in responses] != request_ids:
        raise RuntimeError("Python Host returned responses in the wrong order")
    if not all(item.get("ok") is True for item in responses):
        raise RuntimeError(f"Python Host returned failure: {responses}")

    pids = {item["meta"]["hostPid"] for item in responses}
    if len(pids) != 1:
        raise RuntimeError("logical workers did not share one Python Host process")

    for response in responses:
        print(
            f"OK {response['meta']['worker']} via host pid {response['meta']['hostPid']}: "
            f"{json.dumps(response['data'], ensure_ascii=False)}"
        )


if __name__ == "__main__":
    main()
