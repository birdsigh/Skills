"""Shared sensitive-value detection and redaction rules."""

from __future__ import annotations

import ipaddress
from pathlib import PurePosixPath
import re


IPV4_CANDIDATE = re.compile(r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])")
IPV6_CANDIDATE = re.compile(
    r"(?<![0-9A-Fa-f:.])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:.])"
)
DOCUMENTATION_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32")
)
VERSION_CONTEXT = re.compile(
    r"(?:\b(?:v|ver|version|versions|rev|release|tag)\s*[:=]?\s*|[A-Za-z_]|==|>=|<=|~=|\^|~|@)$"
)
VERSION_SUFFIX = re.compile(r"[-+][A-Za-z][0-9A-Za-z.]*")
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("cloud access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,255}\b")),
    ("live payment key", re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b")),
    ("chat service token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b")),
    ("authorization token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE)),
    (
        "credential assignment",
        re.compile(
            r"\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd)\b"
            r"\s*[:=]\s*[\"']?[^\s\"'`,;]{8,}",
            re.IGNORECASE,
        ),
    ),
    ("credential-bearing URL", re.compile(r"\bhttps?://[^/\s:@]+:[^/\s@]+@", re.IGNORECASE)),
)
SENSITIVE_FILENAMES = {
    ".env",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "id_dsa",
    "id_ed25519",
    "id_ecdsa",
    "id_rsa",
}
GENERATED_COMPONENTS = {
    ".next",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
}
GENERATED_FILENAMES = {".DS_Store"}
GENERATED_SUFFIXES = {".class", ".o", ".obj", ".pyc", ".pyo"}


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def local_ip(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        address.is_loopback
        or address.is_unspecified
        or address.is_private
        or address.is_link_local
        or any(address in network for network in DOCUMENTATION_NETWORKS)
    )


def version_literal(match: re.Match[str]) -> bool:
    text = match.string
    before = text[max(0, match.start() - 32) : match.start()]
    return bool(VERSION_CONTEXT.search(before) or VERSION_SUFFIX.match(text, match.end()))


def blocking_ip(match: re.Match[str]) -> bool:
    try:
        address = ipaddress.ip_address(match.group())
    except ValueError:
        return False
    return not local_ip(address) and not version_literal(match)


def text_findings(text: str) -> set[tuple[str, int]]:
    matches: set[tuple[str, int]] = set()
    for category, pattern in (("IPv4 address", IPV4_CANDIDATE), ("IPv6 address", IPV6_CANDIDATE)):
        for match in pattern.finditer(text):
            if blocking_ip(match):
                matches.add((category, line_number(text, match.start())))

    for category, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            matches.add((category, line_number(text, match.start())))
    return matches


def path_findings(path: str) -> set[tuple[str, int]]:
    findings = text_findings(path)
    pure_path = PurePosixPath(path)
    parts = set(pure_path.parts)
    name = pure_path.name
    if name in SENSITIVE_FILENAMES or (name.startswith(".env.") and not name.endswith((".example", ".sample", ".template"))):
        findings.add(("sensitive filename", 1))
    if parts & GENERATED_COMPONENTS or name in GENERATED_FILENAMES or pure_path.suffix.lower() in GENERATED_SUFFIXES:
        findings.add(("generated artifact", 1))
    return findings


def redact(text: str) -> str:
    redacted = text
    for pattern in (IPV4_CANDIDATE, IPV6_CANDIDATE):
        redacted = pattern.sub(
            lambda match: "[REDACTED]" if blocking_ip(match) else match.group(),
            redacted,
        )
    for _category, pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted
