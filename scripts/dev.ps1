$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==> [1/4] Installing npm workspace dependencies"
npm install

Write-Host "==> [2/4] Synchronizing the Python uv workspace"
uv sync --directory python --all-packages --all-groups

Write-Host "==> [3/4] Checking the local toolchain"
npm run doctor

Write-Host "==> [4/4] Building the persistent Python Host and opening Tauri"
npm run dev
