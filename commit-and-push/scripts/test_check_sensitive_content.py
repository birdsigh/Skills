#!/usr/bin/env python3
"""Integration and classification tests for check-sensitive-content.py."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("check-sensitive-content.py")
SPEC = importlib.util.spec_from_file_location("check_sensitive_content", SCRIPT)
assert SPEC and SPEC.loader
scanner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = scanner
SPEC.loader.exec_module(scanner)


def joined(*parts: str) -> str:
    return "".join(parts)


PUBLIC_V4 = joined("8.8", ".8.8")
PUBLIC_V6 = joined("2606:4700:4700:", ":1111")
SECRET = joined("gh", "p_abcdefghijklmnopqrstuvwxyz0123456789")


class ScannerRepository(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / "base.txt").write_text("base\n")
        self.git("add", "base.txt")
        self.git("commit", "-qm", "base")

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(("git", *args), cwd=self.repo, check=True, capture_output=True)

    def write(self, path: str, data: bytes):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def scan(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            (sys.executable, str(SCRIPT), *args),
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_utf8_routable_addresses_are_blocked(self):
        for name, address, category in (
            ("source.swift", PUBLIC_V4, "IPv4 address"),
            ("notes.md", PUBLIC_V6, "IPv6 address"),
        ):
            with self.subTest(name=name):
                self.write(name, address.encode())
                result = self.scan("--worktree")
                self.assertEqual(result.returncode, 1)
                self.assertIn(category, result.stderr)
                (self.repo / name).unlink()

    def test_amber_style_png_and_jpeg_binary_noise_is_allowed(self):
        fixtures = (
            ("marketing/example.png", b"\x89PNG\r\n\x1a\n\x00" + PUBLIC_V6.encode()),
            ("marketing/example.jpg", b"\xff\xd8\xff\x00" + SECRET.encode() + b"\xff\xd9"),
        )
        for path, data in fixtures:
            with self.subTest(path=path):
                self.write(path, data)
                result = self.scan("--worktree", "--verbose")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("binary content, text rules skipped", result.stderr)
                (self.repo / path).unlink()

    def test_binary_archive_is_blocked(self):
        self.write("bundle.bin", b"PK\x03\x04\x00" + PUBLIC_V6.encode())
        result = self.scan("--worktree")
        self.assertEqual(result.returncode, 1)
        self.assertIn("archive file", result.stderr)

    def test_oversized_binary_is_blocked(self):
        self.write("large.bin", b"\x00\xff")
        result = self.scan("--worktree", "--max-bytes", "1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("oversized file", result.stderr)

    def test_binary_path_checks_are_preserved(self):
        for path, category in (
            (".env", "sensitive filename"),
            ("build/output.bin", "generated artifact"),
            (f"host-{PUBLIC_V4}.bin", "IPv4 address"),
        ):
            with self.subTest(path=path):
                self.write(path, b"\x00\xff")
                result = self.scan("--worktree")
                self.assertEqual(result.returncode, 1)
                self.assertIn(category, result.stderr)
                (self.repo / path).unlink()

    def test_commit_metadata_is_always_scanned(self):
        self.write("committed.txt", b"safe\n")
        self.git("add", "committed.txt")
        self.git("commit", "-qm", f"metadata {PUBLIC_V4} {SECRET}")
        result = self.scan("--range", "HEAD^..HEAD")
        self.assertEqual(result.returncode, 1)
        self.assertIn("commit ", result.stderr)
        self.assertTrue("IPv4 address" in result.stderr or "GitHub token" in result.stderr)

    def test_force_text_applies_text_rules(self):
        self.write("forced.dat", b"\x00" + PUBLIC_V4.encode())
        automatic = self.scan("--worktree")
        forced = self.scan("--worktree", "--force-text", "*.dat")
        self.assertEqual(automatic.returncode, 0, automatic.stderr)
        self.assertEqual(forced.returncode, 1)
        self.assertIn("IPv4 address", forced.stderr)

    def test_default_success_is_quiet(self):
        self.write("image.png", b"\x89PNG\x00noise")
        result = self.scan("--worktree")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout + result.stderr, "")


class ClassificationTests(unittest.TestCase):
    def test_empty_files_are_text(self):
        self.assertTrue(scanner.is_probably_text(b""))

    def test_nul_data_is_binary(self):
        self.assertFalse(scanner.is_probably_text(b"hello\x00world"))

    def test_invalid_utf8_is_consistently_binary(self):
        data = b"\xff\xfe\xfa"
        self.assertFalse(scanner.is_probably_text(data))
        self.assertFalse(scanner.is_probably_text(data))

    def test_utf16_bom_text_is_scanned(self):
        data = PUBLIC_V4.encode("utf-16")
        self.assertTrue(scanner.is_probably_text(data))
        self.assertIn(("IPv4 address", 1), scanner.blob_findings(data))

    def test_blob_read_failure_fails_closed(self):
        args = argparse.Namespace(
            staged=False,
            revision_range=None,
            worktree=True,
            max_bytes=scanner.DEFAULT_MAX_BYTES,
            verbose=False,
            force_text=[],
        )
        with (
            mock.patch.object(scanner, "parse_args", return_value=args),
            mock.patch.object(scanner, "worktree_paths", return_value=["broken.bin"]),
            mock.patch.object(scanner.Path, "lstat", side_effect=OSError("unreadable")),
        ):
            self.assertEqual(scanner.main(), 2)


if __name__ == "__main__":
    unittest.main()
