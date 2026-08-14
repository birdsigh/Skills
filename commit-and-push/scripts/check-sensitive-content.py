#!/usr/bin/env python3
"""Block sensitive values and suspicious artifacts in Git changes."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

from sensitive_rules import path_findings, redact, text_findings


DEFAULT_MAX_BYTES = 10 * 1024 * 1024
ARCHIVE_SIGNATURES = (
    b"PK\x03\x04",
    b"\x1f\x8b",
    b"BZh",
    b"\xfd7zXZ\x00",
    b"7z\xbc\xaf\x27\x1c",
    b"Rar!\x1a\x07",
)
BINARY_SIGNATURES = (
    b"%PDF-",
    b"\x89PNG\r\n\x1a\n",
    b"\xff\xd8\xff",
    b"GIF87a",
    b"GIF89a",
    b"BM",
    b"II*\x00",
    b"MM\x00*",
    b"\x7fELF",
    b"MZ",
    b"SQLite format 3\x00",
)


def git(*args: str) -> bytes:
    result = subprocess.run(
        ("git", *args),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result.stdout


def changed_paths(staged: bool, revision_range: str | None) -> list[str]:
    args = ["diff"]
    if staged:
        args.append("--cached")
    elif revision_range is not None:
        args.append(revision_range)
    args.extend(("--name-only", "--diff-filter=ACMR", "-z", "--"))
    raw_paths = git(*args)
    return [path.decode("utf-8", errors="surrogateescape") for path in raw_paths.split(b"\0") if path]


def worktree_paths() -> list[str]:
    tokens = git("status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    paths: list[str] = []
    index = 0
    while index < len(tokens) and tokens[index]:
        record = tokens[index]
        index += 1
        status = record[:2].decode("ascii", errors="replace")
        path = record[3:].decode("utf-8", errors="surrogateescape")
        if "R" in status or "C" in status:
            index += 1
        if "D" not in status and os.path.lexists(Path.cwd() / path):
            paths.append(path)
    return paths


def revision(path: str, staged: bool) -> str:
    return f":{path}" if staged else f"HEAD:{path}"


def blob_size(path: str, staged: bool) -> int:
    return int(git("cat-file", "-s", revision(path, staged)).strip())


def blob(path: str, staged: bool) -> bytes:
    return git("show", "--no-textconv", revision(path, staged))


def worktree_blob(path: str) -> bytes:
    target = Path.cwd() / path
    if target.is_symlink():
        return os.readlink(target).encode("utf-8", errors="surrogateescape")
    return target.read_bytes()


def outgoing_commit_findings(revision_range: str) -> list[tuple[str, str, int]]:
    matches: list[tuple[str, str, int]] = []
    for raw_sha in git("rev-list", revision_range).splitlines():
        sha = raw_sha.decode("ascii")
        metadata = git("show", "-s", "--format=%an%n%ae%n%cn%n%ce%n%B", sha).decode(
            "utf-8", errors="replace"
        )
        for category, line in text_findings(metadata):
            matches.append((sha[:12], category, line))
    return matches


def is_archive(data: bytes) -> bool:
    return any(data.startswith(signature) for signature in ARCHIVE_SIGNATURES) or (
        len(data) > 262 and data[257:262] == b"ustar"
    )


def is_binary(data: bytes) -> bool:
    if any(data.startswith(signature) for signature in BINARY_SIGNATURES):
        return True
    sample = data[:8192]
    if b"\x00" in sample:
        return True
    try:
        decoded = sample.decode("utf-8")
    except UnicodeDecodeError:
        return True
    disallowed_controls = sum(ord(character) < 32 and character not in "\b\t\n\f\r" for character in decoded)
    return bool(decoded) and disallowed_controls / len(decoded) > 0.01


def blob_findings(data: bytes) -> set[tuple[str, int]]:
    matches: set[tuple[str, int]] = set()
    if is_archive(data):
        matches.add(("archive file", 1))
    elif is_binary(data):
        matches.add(("binary file", 1))
    matches.update(text_findings(data.decode("utf-8", errors="replace")))
    return matches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--range", dest="revision_range")
    mode.add_argument("--worktree", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    args = parser.parse_args()
    if args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    return args


def main() -> int:
    args = parse_args()
    try:
        blocked = False
        if args.revision_range:
            for sha, category, line in outgoing_commit_findings(args.revision_range):
                print(f"blocked: commit {sha}:{line}: {category}", file=sys.stderr)
                blocked = True

        paths = worktree_paths() if args.worktree else changed_paths(args.staged, args.revision_range)
        for path in paths:
            findings = path_findings(path)
            size = (Path.cwd() / path).lstat().st_size if args.worktree else blob_size(path, args.staged)
            if size > args.max_bytes:
                findings.add(("oversized file", 1))
            else:
                data = worktree_blob(path) if args.worktree else blob(path, args.staged)
                findings.update(blob_findings(data))
            safe_path = redact(path)
            for category, line in sorted(findings):
                print(f"blocked: {safe_path}:{line}: {category}", file=sys.stderr)
                blocked = True
        return 1 if blocked else 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"sensitive-content scan failed: {redact(str(error))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
