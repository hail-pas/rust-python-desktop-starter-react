from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_toml(path: Path):
    with path.open("rb") as file:
        return tomllib.load(file)


def main() -> None:
    root_package = load_json(ROOT / "package.json")
    assert root_package["version"] == "0.5.0"
    assert root_package["packageManager"] == "npm@11.17.0"
    assert root_package["engines"] == {"node": ">=24.18.0", "npm": ">=11.17.0"}
    assert set(root_package["workspaces"]) == {"apps/desktop", "frontend"}

    doctor = (ROOT / "scripts/doctor.mjs").read_text(encoding="utf-8")
    expected_requirements = {
        "node": (24, 18, 0),
        "npm": (11, 17, 0),
        "uv": (0, 11, 3),
        "rustc": (1, 97, 1),
        "cargo": (1, 97, 1),
    }
    for command, version in expected_requirements.items():
        minimum = ", ".join(map(str, version))
        pattern = rf'command: "{command}"[^\n]+minimum: \[{minimum}\]'
        assert re.search(pattern, doctor), f"doctor requirement missing: {command} {version}"

    frontend = load_json(ROOT / "frontend/package.json")
    assert frontend["version"] == "0.5.0"
    assert frontend["engines"] == root_package["engines"]
    assert frontend["dependencies"] == {
        "@tauri-apps/api": "2.11.1",
        "react": "19.2.8",
        "react-dom": "19.2.8",
    }
    assert frontend["devDependencies"] == {
        "@types/react": "19.2.17",
        "@types/react-dom": "19.2.3",
        "@vitejs/plugin-react": "6.0.3",
        "typescript": "7.0.2",
        "vite": "8.1.5",
    }

    desktop_package = load_json(ROOT / "apps/desktop/package.json")
    assert desktop_package["version"] == "0.5.0"
    assert desktop_package["engines"] == root_package["engines"]
    assert desktop_package["devDependencies"] == {"@tauri-apps/cli": "2.11.4"}

    cargo = load_toml(ROOT / "Cargo.toml")
    expected_cargo_members = {
        "apps/desktop/src-tauri",
        "crates/app-contracts",
        "crates/app-core",
        "crates/python-host",
    }
    assert set(cargo["workspace"]["members"]) == expected_cargo_members
    assert cargo["workspace"]["resolver"] == "3"
    assert cargo["workspace"]["package"]["version"] == "0.5.0"
    assert cargo["workspace"]["package"]["edition"] == "2024"
    assert cargo["workspace"]["package"]["rust-version"] == "1.97"
    assert cargo["workspace"]["dependencies"]["tauri"] == "=2.11.5"
    assert cargo["workspace"]["dependencies"]["tauri-plugin-shell"] == "=2.3.5"

    rust_toolchain = load_toml(ROOT / "rust-toolchain.toml")
    assert rust_toolchain["toolchain"]["channel"] == "1.97.1"

    python = load_toml(ROOT / "python/pyproject.toml")
    assert python["project"]["version"] == "0.5.0"
    assert python["project"]["requires-python"] == ">=3.13,<3.15"
    assert set(python["tool"]["uv"]["workspace"]["members"]) == {
        "host",
        "packages/*",
        "workers/*",
    }
    assert (ROOT / "python/.python-version").read_text().strip() == "3.13.11"
    uv_config = load_toml(ROOT / "python/uv.toml")
    assert uv_config["required-version"] == ">=0.11.3"

    package_manifests = [
        ROOT / "python/host/pyproject.toml",
        ROOT / "python/packages/worker-common/pyproject.toml",
    ]
    package_manifests.extend(sorted((ROOT / "python/workers").glob("*/pyproject.toml")))
    logical_workers: set[str] = set()
    for manifest in package_manifests:
        config = load_toml(manifest)
        assert config["project"]["version"] == "0.5.0"
        assert config["project"]["requires-python"] == ">=3.13,<3.15"
        assert config["build-system"] == {
            "requires": ["uv_build==0.11.31"],
            "build-backend": "uv_build",
        }
        worker = config.get("tool", {}).get("starter", {}).get("worker")
        if worker:
            logical_workers.add(worker["name"])
    assert logical_workers == {"greeter", "statistics"}

    host = load_toml(ROOT / "python/host/pyproject.toml")
    assert host["tool"]["starter"]["host"] == {
        "binary-name": "python-host",
        "module": "starter_python_host.__main__",
    }
    assert set(host["project"]["dependencies"]) == {
        "starter-worker-common",
        "starter-worker-greeter",
        "starter-worker-statistics",
    }

    tauri = load_json(ROOT / "apps/desktop/src-tauri/tauri.conf.json")
    assert tauri["version"] == "0.5.0"
    assert tauri["bundle"]["externalBin"] == ["binaries/python-host"]

    capability = load_json(ROOT / "apps/desktop/src-tauri/capabilities/default.json")
    spawn_permissions = [
        permission
        for permission in capability["permissions"]
        if isinstance(permission, dict) and permission.get("identifier") == "shell:allow-spawn"
    ]
    assert len(spawn_permissions) == 1
    assert spawn_permissions[0]["allow"] == [
        {"name": "binaries/python-host", "sidecar": True}
    ]

    registry = (ROOT / "python/host/src/starter_python_host/registry.py").read_text(
        encoding="utf-8"
    )
    for worker in logical_workers:
        assert f'"{worker}"' in registry

    print("OK: one Python Host, two logical workers, and toolchain constraints are consistent")


if __name__ == "__main__":
    main()
