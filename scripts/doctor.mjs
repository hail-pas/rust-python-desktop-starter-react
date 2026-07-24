import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const requirements = [
  { command: "node", args: ["--version"], minimum: [24, 18, 0] },
  { command: "npm", args: ["--version"], minimum: [11, 17, 0] },
  { command: "uv", args: ["--version"], minimum: [0, 11, 3] },
  { command: "rustc", args: ["--version"], minimum: [1, 97, 1] },
  { command: "cargo", args: ["--version"], minimum: [1, 97, 1] },
];

function parseVersion(output) {
  const match = output.match(/(\d+)\.(\d+)\.(\d+)/);
  return match ? match.slice(1).map(Number) : null;
}

function isAtLeast(actual, minimum) {
  for (let index = 0; index < minimum.length; index += 1) {
    if (actual[index] > minimum[index]) return true;
    if (actual[index] < minimum[index]) return false;
  }
  return true;
}

function invocationFor(requirement) {
  if (requirement.command === "npm" && process.env.npm_execpath) {
    return {
      command: process.execPath,
      args: [process.env.npm_execpath, ...requirement.args],
    };
  }
  return requirement;
}

let failed = false;
for (const requirement of requirements) {
  try {
    const invocation = invocationFor(requirement);
    const output = execFileSync(invocation.command, invocation.args, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "inherit"],
    }).trim();
    const version = parseVersion(output);
    if (!version || !isAtLeast(version, requirement.minimum)) {
      failed = true;
      console.error(
        `ERR ${requirement.command}: ${output}; required >= ${requirement.minimum.join(".")}`,
      );
      continue;
    }
    console.log(`OK  ${requirement.command}: ${output}`);
  } catch {
    failed = true;
    console.error(`ERR ${requirement.command}: not available on PATH`);
  }
}

const requiredFiles = [
  ".nvmrc",
  "rust-toolchain.toml",
  "frontend/package.json",
  "apps/desktop/src-tauri/tauri.conf.json",
  "python/pyproject.toml",
  "python/host/pyproject.toml",
  "python/.python-version",
  "python/uv.toml",
  "Cargo.toml",
];
for (const path of requiredFiles) {
  if (existsSync(join(process.cwd(), path))) {
    console.log(`OK  file: ${path}`);
  } else {
    failed = true;
    console.error(`ERR file: ${path} is missing`);
  }
}

if (failed) process.exitCode = 1;
