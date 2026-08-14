#!/usr/bin/env python3
"""Report repository-owned Git hook configuration without executing hooks."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


CONFIG_PATHS = (
    ".pre-commit-config.yaml",
    ".pre-commit-config.yml",
    "lefthook.yml",
    "lefthook.yaml",
    ".lefthook.yml",
    ".lefthook.yaml",
    ".overcommit.yml",
    ".husky",
    ".githooks",
)
KNOWN_HOOKS = {
    "applypatch-msg",
    "commit-msg",
    "post-applypatch",
    "post-checkout",
    "post-commit",
    "post-merge",
    "post-rewrite",
    "post-update",
    "pre-applypatch",
    "pre-auto-gc",
    "pre-commit",
    "pre-merge-commit",
    "pre-push",
    "pre-rebase",
    "pre-receive",
    "prepare-commit-msg",
    "push-to-checkout",
    "update",
}


def git(*args: str, allow_failure: bool = False) -> str:
    result = subprocess.run(
        ("git", *args),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode and not allow_failure:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip() if result.returncode == 0 else ""


def hook_files(directory: Path) -> list[dict[str, object]]:
    if not directory.is_dir():
        return []
    return [
        {
            "name": path.name,
            "executable": path.is_file() and os.access(path, os.X_OK),
        }
        for path in sorted(directory.iterdir())
        if not path.name.endswith(".sample") and path.name != ".gitignore"
    ]


def package_hook_config(root: Path) -> bool:
    package_json = root / "package.json"
    if not package_json.is_file():
        return False
    try:
        data = json.loads(package_json.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    scripts = data.get("scripts", {})
    commands = scripts.values() if isinstance(scripts, dict) else ()
    return "husky" in data or any("husky" in str(command).lower() for command in commands)


def source_hook_names(directory: Path) -> set[str]:
    if not directory.is_dir():
        return set()
    return {path.name for path in directory.iterdir() if path.is_file() and path.name in KNOWN_HOOKS}


def expected_hooks(root: Path, configs: list[str]) -> set[str]:
    expected: set[str] = set()
    if any(path.startswith(".pre-commit-config.") for path in configs):
        expected.add("pre-commit")
    expected.update(source_hook_names(root / ".husky"))
    expected.update(source_hook_names(root / ".githooks"))
    for name in ("lefthook.yml", "lefthook.yaml", ".lefthook.yml", ".lefthook.yaml"):
        path = root / name
        if not path.is_file():
            continue
        try:
            for line in path.read_text().splitlines():
                candidate = line.split(":", 1)[0].strip()
                if candidate in KNOWN_HOOKS:
                    expected.add(candidate)
        except OSError:
            continue
    return expected


def main() -> int:
    try:
        root = Path(git("rev-parse", "--show-toplevel"))
        configured_path = git("config", "--get", "core.hooksPath", allow_failure=True) or None
        if configured_path:
            candidate = Path(configured_path)
            resolved = candidate if candidate.is_absolute() else root / candidate
        else:
            resolved = Path(git("rev-parse", "--git-path", "hooks"))
            if not resolved.is_absolute():
                resolved = root / resolved

        configs = [path for path in CONFIG_PATHS if (root / path).exists()]
        if package_hook_config(root):
            configs.append("package.json (hook-manager configuration)")
        hooks = hook_files(resolved)
        executable = {str(hook["name"]) for hook in hooks if hook["executable"]}
        expected = expected_hooks(root, configs)
        missing = sorted(expected - executable)

        if not configs and not configured_path and not executable:
            status = "none"
        elif expected and not missing:
            status = "verified-active"
        elif expected:
            status = "inactive-or-unverified"
        else:
            status = "uncertain"

        report = {
            "root": str(root),
            "status": status,
            "coreHooksPath": configured_path,
            "resolvedHooksDirectory": str(resolved),
            "configuration": sorted(configs),
            "expectedHooks": sorted(expected),
            "missingExpectedHooks": missing,
            "hooks": hooks,
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (OSError, RuntimeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
