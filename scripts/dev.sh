#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

echo "==> [1/4] Installing npm workspace dependencies"
npm install

echo "==> [2/4] Synchronizing the Python uv workspace"
uv sync --directory python --all-packages --all-groups

echo "==> [3/4] Checking the local toolchain"
npm run doctor

echo "==> [4/4] Building the persistent Python Host and opening Tauri"
npm run dev
