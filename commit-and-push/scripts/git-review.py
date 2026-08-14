#!/usr/bin/env python3
"""Emit deterministic JSON for commit-and-push repository reviews."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True

from sensitive_rules import redact


def git(*args: str, allow_failure: bool = False) -> bytes:
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    result = subprocess.run(
        ("git", *args),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if result.returncode and not allow_failure:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result.stdout if result.returncode == 0 else b""


def text(*args: str, allow_failure: bool = False) -> str:
    return git(*args, allow_failure=allow_failure).decode("utf-8", errors="replace").strip()


def root() -> Path:
    return Path(text("rev-parse", "--show-toplevel"))


def top_level(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else "(root)"


def summarize(entries: list[dict[str, str | None]]) -> dict[str, object]:
    statuses = Counter(entry["category"] for entry in entries)
    groups = Counter(top_level(str(entry["path"])) for entry in entries)
    return {
        "pathCount": len(entries),
        "largeChange": len(entries) > 50,
        "statusCounts": dict(sorted(statuses.items())),
        "topLevelGroups": dict(sorted(groups.items())),
    }


def status_entries() -> list[dict[str, str | None]]:
    tokens = git("status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    entries: list[dict[str, str | None]] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        record = tokens[index]
        index += 1
        status = record[:2].decode("ascii", errors="replace")
        path = redact(record[3:].decode("utf-8", errors="surrogateescape"))
        original_path = None
        if "R" in status or "C" in status:
            original_path = redact(tokens[index].decode("utf-8", errors="surrogateescape"))
            index += 1

        if status == "??":
            category = "untracked"
        elif "R" in status or "C" in status:
            category = "renamed"
        elif "D" in status:
            category = "deleted"
        elif "A" in status:
            category = "added"
        else:
            category = "modified"
        entries.append(
            {
                "path": path,
                "originalPath": original_path,
                "indexStatus": status[0],
                "worktreeStatus": status[1],
                "category": category,
            }
        )
    return entries


def operations() -> list[str]:
    git_dir = Path(text("rev-parse", "--absolute-git-dir"))
    checks = {
        "merge": git_dir / "MERGE_HEAD",
        "rebase": git_dir / "rebase-merge",
        "rebase-apply": git_dir / "rebase-apply",
        "cherry-pick": git_dir / "CHERRY_PICK_HEAD",
        "revert": git_dir / "REVERT_HEAD",
    }
    return [name for name, path in checks.items() if path.exists()]


def branch_details() -> dict[str, object]:
    remotes = [name for name in text("remote", allow_failure=True).splitlines() if name]
    branch = text("symbolic-ref", "--quiet", "--short", "HEAD", allow_failure=True) or None
    if branch is None:
        return {
            "detached": True,
            "branch": None,
            "upstream": None,
            "remote": None,
            "remoteBranch": None,
            "remoteDefaultBranch": None,
            "remotes": remotes,
        }

    upstream = text("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", allow_failure=True) or None
    remote = text("config", "--get", f"branch.{branch}.remote", allow_failure=True) or None
    merge_ref = text("config", "--get", f"branch.{branch}.merge", allow_failure=True) or None
    remote_branch = merge_ref.removeprefix("refs/heads/") if merge_ref else None
    default_ref = None
    if remote:
        default_ref = text(
            "symbolic-ref",
            "--quiet",
            "--short",
            f"refs/remotes/{remote}/HEAD",
            allow_failure=True,
        ) or None
    default_branch = default_ref.removeprefix(f"{remote}/") if default_ref and remote else None
    return {
        "detached": False,
        "branch": branch,
        "upstream": upstream,
        "remote": remote,
        "remoteBranch": remote_branch,
        "remoteDefaultBranch": default_branch,
        "remotes": remotes,
    }


def gate() -> dict[str, object]:
    repo_root = root()
    conflicts = [
        redact(item.decode("utf-8", errors="surrogateescape"))
        for item in git("diff", "--name-only", "--diff-filter=U", "-z").split(b"\0")
        if item
    ]
    return {
        "root": str(repo_root),
        **branch_details(),
        "operations": operations(),
        "conflicts": conflicts,
    }


def inspect() -> dict[str, object]:
    state = gate()
    if state["operations"] or state["conflicts"] or state["detached"]:
        return {**state, "worktree": None}
    entries = status_entries()
    return {
        **state,
        "worktree": {**summarize(entries), "paths": entries},
    }


def outgoing_entries(upstream: str) -> list[dict[str, str | None]]:
    tokens = git("diff", "--name-status", "-z", "-M", "-C", f"{upstream}..HEAD", "--").split(b"\0")
    entries: list[dict[str, str | None]] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        status = tokens[index].decode("ascii", errors="replace")
        index += 1
        original_path = None
        if status.startswith(("R", "C")):
            original_path = redact(tokens[index].decode("utf-8", errors="surrogateescape"))
            path = redact(tokens[index + 1].decode("utf-8", errors="surrogateescape"))
            index += 2
            category = "renamed"
        else:
            path = redact(tokens[index].decode("utf-8", errors="surrogateescape"))
            index += 1
            category = {
                "A": "added",
                "D": "deleted",
                "M": "modified",
                "T": "modified",
            }.get(status[:1], "modified")
        entries.append(
            {
                "path": path,
                "originalPath": original_path,
                "status": status,
                "category": category,
            }
        )
    return entries


def diff_totals(upstream: str) -> tuple[int, int]:
    shortstat = text("diff", "--shortstat", f"{upstream}..HEAD", "--")
    insertions = re.search(r"(\d+) insertion", shortstat)
    deletions = re.search(r"(\d+) deletion", shortstat)
    return (int(insertions.group(1)) if insertions else 0, int(deletions.group(1)) if deletions else 0)


def outgoing() -> dict[str, object]:
    details = branch_details()
    upstream = details["upstream"]
    remote = details["remote"]
    remote_branch = details["remoteBranch"]
    if details["detached"]:
        raise RuntimeError("HEAD is detached")
    if not upstream or not remote or not remote_branch:
        raise RuntimeError("current branch has no complete configured upstream")

    counts = text("rev-list", "--left-right", "--count", f"{upstream}...HEAD").split()
    behind, ahead = (int(counts[0]), int(counts[1]))
    records = git("log", "-z", "--format=%H%x1f%s", f"{upstream}..HEAD").split(b"\0")
    commits = []
    for record in records:
        if not record:
            continue
        sha, subject = record.decode("utf-8", errors="replace").split("\x1f", 1)
        commits.append({"sha": sha, "subject": subject})

    entries = outgoing_entries(str(upstream))
    insertions, deletions = diff_totals(str(upstream))
    destination_is_default = remote_branch == details["remoteDefaultBranch"]
    return {
        **details,
        "behind": behind,
        "ahead": ahead,
        "diverged": behind > 0 and ahead > 0,
        "destinationIsDefaultBranch": destination_is_default,
        "commits": commits,
        "changes": {**summarize(entries), "insertions": insertions, "deletions": deletions, "paths": entries},
        "pushCommand": f"git push {shlex.quote(str(remote))} HEAD:{shlex.quote(str(remote_branch))}",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("gate", "inspect", "outgoing"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = {"gate": gate, "inspect": inspect, "outgoing": outgoing}[args.mode]()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
