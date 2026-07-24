from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from worker_manifest import discover_host, discover_workers

PYTHON_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PYTHON_ROOT.parent
BUILD_ROOT = PYTHON_ROOT / "build" / "pyinstaller"
WORK_ROOT = BUILD_ROOT / "work"
SPEC_ROOT = BUILD_ROOT / "specs"
DIST_ROOT = PYTHON_ROOT / "dist"
SIDECAR_ROOT = REPOSITORY_ROOT / "apps" / "desktop" / "src-tauri" / "binaries"


def rust_target_triple() -> str:
    override = os.environ.get("TAURI_ENV_TARGET_TRIPLE") or os.environ.get("TARGET_TRIPLE")
    if override:
        return override

    try:
        result = subprocess.run(
            ["rustc", "--print", "host-tuple"],
            check=True,
            capture_output=True,
            text=True,
        )
        target = result.stdout.strip()
        if target:
            return target
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    system = platform.system().lower()
    machine = platform.machine().lower()
    normalized_machine = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "arm64": "aarch64",
        "aarch64": "aarch64",
    }.get(machine)
    if normalized_machine is None:
        raise RuntimeError(f"unsupported CPU architecture: {machine}")

    if system == "windows":
        return f"{normalized_machine}-pc-windows-msvc"
    if system == "darwin":
        return f"{normalized_machine}-apple-darwin"
    if system == "linux":
        return f"{normalized_machine}-unknown-linux-gnu"
    raise RuntimeError(f"unsupported operating system: {system}")


def write_entrypoint(module: str, binary_name: str) -> Path:
    entrypoint_directory = BUILD_ROOT / "entrypoints"
    entrypoint_directory.mkdir(parents=True, exist_ok=True)
    entrypoint = entrypoint_directory / f"{binary_name}.py"
    entrypoint.write_text(
        f"from {module} import main\n\nif __name__ == '__main__':\n    main()\n",
        encoding="utf-8",
    )
    return entrypoint


def build_input() -> tuple[str, list[str]]:
    request_ids: list[str] = []
    lines: list[str] = []
    for index, worker in enumerate(discover_workers(), start=1):
        request_id = f"binary-smoke-{index}"
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


def smoke_binary(binary: Path) -> None:
    stdin, request_ids = build_input()
    result = subprocess.run(
        [str(binary)],
        input=stdin,
        check=False,
        capture_output=True,
        encoding="utf-8",
        timeout=90,
    )
    if result.returncode != 0:
        raise RuntimeError(f"built Python Host failed smoke test: {result.stderr.strip()}")

    responses = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    if [item.get("requestId") for item in responses] != request_ids:
        raise RuntimeError(f"built Python Host returned invalid responses: {responses}")
    if not all(item.get("ok") is True for item in responses):
        raise RuntimeError(f"built Python Host returned failure: {responses}")
    if len({item["meta"]["hostPid"] for item in responses}) != 1:
        raise RuntimeError("built logical workers did not share one Python Host process")


def main() -> None:
    host = discover_host()
    target = rust_target_triple()
    entrypoint = write_entrypoint(host.module, host.binary_name)
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    DIST_ROOT.mkdir(parents=True, exist_ok=True)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    SPEC_ROOT.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--noupx",
        "--onefile",
        "--name",
        host.binary_name,
        "--distpath",
        str(DIST_ROOT),
        "--workpath",
        str(WORK_ROOT),
        "--specpath",
        str(SPEC_ROOT),
        str(entrypoint),
    ]
    print(f"Building persistent {host.binary_name} for {target} ...", flush=True)
    subprocess.run(command, cwd=PYTHON_ROOT, check=True)

    extension = ".exe" if os.name == "nt" else ""
    source = DIST_ROOT / f"{host.binary_name}{extension}"
    destination = SIDECAR_ROOT / f"{host.binary_name}-{target}{extension}"
    if not source.is_file():
        raise FileNotFoundError(f"PyInstaller output not found: {source}")

    SIDECAR_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if os.name != "nt":
        destination.chmod(destination.stat().st_mode | 0o111)

    smoke_binary(destination)
    print(f"Built and smoke-tested: {destination.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()
