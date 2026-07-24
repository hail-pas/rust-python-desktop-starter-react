from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

PYTHON_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class WorkerDefinition:
    package_name: str
    name: str
    module: str
    sample_request: str
    project_directory: Path


@dataclass(frozen=True)
class HostDefinition:
    package_name: str
    binary_name: str
    module: str
    project_directory: Path


def discover_workers() -> tuple[WorkerDefinition, ...]:
    definitions: list[WorkerDefinition] = []
    for pyproject in sorted((PYTHON_ROOT / "workers").glob("*/pyproject.toml")):
        with pyproject.open("rb") as file:
            config = tomllib.load(file)

        project = config.get("project", {})
        worker = config.get("tool", {}).get("starter", {}).get("worker", {})
        try:
            definition = WorkerDefinition(
                package_name=str(project["name"]),
                name=str(worker["name"]),
                module=str(worker["module"]),
                sample_request=str(worker["sample-request"]),
                project_directory=pyproject.parent,
            )
        except KeyError as error:
            raise RuntimeError(f"invalid worker manifest {pyproject}: missing {error}") from error
        definitions.append(definition)

    if not definitions:
        raise RuntimeError("no logical Python workers were discovered")

    names = [item.name for item in definitions]
    if len(names) != len(set(names)):
        raise RuntimeError("logical worker names must be unique")

    return tuple(definitions)


def discover_host() -> HostDefinition:
    pyproject = PYTHON_ROOT / "host" / "pyproject.toml"
    with pyproject.open("rb") as file:
        config = tomllib.load(file)

    project = config.get("project", {})
    host = config.get("tool", {}).get("starter", {}).get("host", {})
    try:
        return HostDefinition(
            package_name=str(project["name"]),
            binary_name=str(host["binary-name"]),
            module=str(host["module"]),
            project_directory=pyproject.parent,
        )
    except KeyError as error:
        raise RuntimeError(f"invalid host manifest {pyproject}: missing {error}") from error
