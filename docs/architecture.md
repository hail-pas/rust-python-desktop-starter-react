# Architecture

```text
React/Vite frontend
        │ Tauri invoke
        ▼
apps/desktop/src-tauri
        │ composition root only
        ├── app-core
        ├── app-contracts
        └── PythonHostManager
                │ one persistent stdin/stdout channel
                ▼
        python-host process
                ├── greeter logical worker
                └── statistics logical worker
```

## Boundaries

- `frontend/` owns React UI and TypeScript contracts.
- `apps/desktop/src-tauri/` owns Tauri setup and thin commands.
- `crates/app-core/` owns reusable pure Rust business logic.
- `crates/app-contracts/` owns serialization DTOs.
- `crates/python-host/` owns the persistent Sidecar lifecycle and protocol.
- `python/host/` owns routing and the single Runtime process.
- `python/workers/*` are independently packaged uv workspace members and expose handlers.

## Default concurrency model

Calls are serialized through a Rust async mutex. One request line is written, then one response line is read. This is intentionally simple and deterministic. Later, the protocol can be upgraded to a background reader plus a `requestId -> oneshot sender` pending map for concurrent in-flight requests without changing the logical Worker packages.

## Failure model

Protocol, timeout, stream, or process errors invalidate the current Host process. The manager kills it and lazily creates a new Host on the next call. A normal worker validation error does not restart the Host.
