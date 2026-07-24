# Rust + Python Desktop Starter

A Windows/macOS starter using React + Tauri 2, a modular Cargo workspace, and one persistent Python Host containing multiple logical Workers managed by a uv workspace.

## Why this version is faster

The previous demo launched a new PyInstaller executable for every button click. This version starts `python-host` lazily on the first Python call and keeps it alive. `greeter` and `statistics` are logical handlers inside that process, so later calls reuse the same interpreter, imports, cache, and Host PID.

Because the Host is packaged with PyInstaller `onefile`, the first Python call can still include a one-time extraction and interpreter startup delay. Subsequent calls reuse the already-running Host and should be substantially faster. The UI shows the Host PID so this behavior is easy to verify.

## Directory layout

```text
apps/desktop/src-tauri/     Tauri shell and composition root
frontend/                   React + TypeScript + Vite
crates/app-contracts/       Rust DTOs
crates/app-core/            Pure Rust business logic
crates/python-host/         Persistent Sidecar manager
python/host/                Python Host and routing
python/packages/             Shared Python packages
python/workers/greeter/     Logical Worker package 1
python/workers/statistics/  Logical Worker package 2
```

## Required local tools

`npm run doctor` enforces these minimum versions:

```js
const requirements = [
  { command: "node", args: ["--version"], minimum: [24, 18, 0] },
  { command: "npm", args: ["--version"], minimum: [11, 17, 0] },
  { command: "uv", args: ["--version"], minimum: [0, 11, 3] },
  { command: "rustc", args: ["--version"], minimum: [1, 97, 1] },
  { command: "cargo", args: ["--version"], minimum: [1, 97, 1] },
];
```

The included `.nvmrc` selects Node 26.5.0. The npm engine constraint is `>=11.17.0`; it does not incorrectly require npm 12.

## Run on macOS

```bash
nvm use
./scripts/dev.sh
```

## Run on Windows PowerShell

```powershell
nvm use
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```

The script installs npm dependencies, syncs the uv workspace, runs the doctor, builds one `python-host` Sidecar, smoke-tests both logical Workers inside that same process, and starts Tauri.

## Faster subsequent development

After `python-host` has already been built:

```bash
npm run dev:fast
```

Rebuild the Host whenever Python code or Python dependencies change:

```bash
npm run python:build
```

## Tests and checks

```bash
npm run validate:structure
npm run frontend:typecheck
npm run python:test
npm run python:smoke
npm run python:lint
npm run rust:test
```

The smoke test sends two newline-delimited JSON requests to one Host process and asserts that Greeter and Statistics return the same `hostPid`.

## Build a desktop application

```bash
npm run build
```

Development-only native compile without creating an installer:

```bash
npm run verify:native
```

## Protocol

Rust writes one line:

```json
{"requestId":"rust-123-1","worker":"greeter","payload":{"name":"Ada"}}
```

Python returns one line:

```json
{"requestId":"rust-123-1","ok":true,"data":{"greeting":"..."},"error":null,"meta":{"host":"python-host","hostPid":12345,"worker":"greeter","protocolVersion":1}}
```

stdout is reserved for protocol messages. Python logs must go to stderr.

## Add another logical Worker

1. Copy one directory under `python/workers/`.
2. Give the package a unique `[tool.starter.worker].name`.
3. Implement `handler.handle(payload)`.
4. Add the package to `python/host/pyproject.toml` dependencies and uv sources.
5. Register its handler in `python/host/src/starter_python_host/registry.py`.
6. Add Rust/TypeScript DTOs and a thin Tauri command.

No new Sidecar executable, Python Runtime, Tauri `externalBin`, or shell permission is required.
