# Validation notes

The project includes checks for:

- npm/Cargo/uv workspace membership and version consistency;
- exactly one Tauri external binary named `python-host`;
- `shell:allow-spawn` capability for that Host;
- two logical Worker manifests registered by the Host;
- a source smoke test that sends both requests through one Python process;
- a built-binary smoke test that verifies both responses have the same Host PID;
- Windows and macOS native CI compilation.

The generation environment used for this archive does not contain the required Rust toolchain or the current npm/Python dependency caches, so native Tauri compilation is delegated to the included CI and the user's configured machine. Python source handlers, Host routing, syntax, JSON/TOML parsing, and structural assertions are run locally before packaging.
