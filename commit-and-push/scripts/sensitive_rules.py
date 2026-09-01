"""Shared sensitive-value detection and redaction rules."""

from __future__ import annotations

import ipaddress
from pathlib import PurePosixPath
import re


IPV4_CANDIDATE = re.compile(r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9]|\.[0-9])")
IPV6_CANDIDATE = re.compile(
    r"(?<![0-9A-Fa-f:.])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:.])"
)
CSS_PSEUDO_ELEMENT = re.compile(
    r"::(?:after|backdrop|before|cue|cue-region|file-selector-button|first-letter|first-line|"
    r"grammar-error|marker|part|placeholder|selection|slotted|spelling-error|target-text)"
    r"(?![A-Za-z0-9_-])",
    re.IGNORECASE,
)
DOCUMENTATION_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32")
)
VERSION_CONTEXT = re.compile(
    r"(?:\b(?:v|ver|version|versions|rev|release|tag)\s*[:=]?\s*|[A-Za-z_]|==|>=|<=|~=|\^|~|@)$"
)
VERSION_SUFFIX = re.compile(r"[-+][A-Za-z][0-9A-Za-z.]*")
SENSITIVE_PROPERTY = (
    r"(?:x[-_]?api[-_]?key|api[-_]?key|access[-_]?token|auth[-_]?token|"
    r"client[-_]?secret|password|passwd|token|secret|key|authorization)"
)
QUOTED_CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?:[\"']" + SENSITIVE_PROPERTY + r"[\"']|\b" + SENSITIVE_PROPERTY + r"\b)"
    r"\s*[:=]\s*(?:"
    r'"(?P<double>(?:\\.|[^"\\\n])*)"'
    r"|'(?P<single>(?:\\.|[^'\\\n])*)'"
    r"|`(?P<template>(?:\\.|[^`\\\n])*)`"
    r")",
    re.IGNORECASE,
)
JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
SK_TOKEN = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")
GOOGLE_API_KEY = re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b")
OPAQUE_HEX_TOKEN = re.compile(r"[A-Fa-f0-9]{32,}")
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("cloud access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,255}\b")),
    ("live payment key", re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b")),
    ("chat service token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b")),
    ("JSON web token", JWT),
    ("API key", SK_TOKEN),
    ("Google API key", GOOGLE_API_KEY),
    ("authorization token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE)),
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


def css_pseudo_element(match: re.Match[str]) -> bool:
    """Return whether an IPv6-shaped prefix is part of a CSS pseudo-element."""
    return bool(CSS_PSEUDO_ELEMENT.match(match.string, match.start()))


def high_entropy(value: str) -> bool:
    """Identify long token-like values without treating identifiers as credentials."""
    if len(value) < 24 or any(character.isspace() for character in value):
        return False
    classes = sum(
        (
            any(character.islower() for character in value),
            any(character.isupper() for character in value),
            any(character.isdigit() for character in value),
            any(character in "._~+/=-" for character in value),
        )
    )
    return classes >= 3


def credential_literal(value: str) -> bool:
    """Return whether a static quoted value is credential-like."""
    if "${" in value:
        return False
    return bool(
        JWT.fullmatch(value)
        or SK_TOKEN.fullmatch(value)
        or GOOGLE_API_KEY.fullmatch(value)
        or OPAQUE_HEX_TOKEN.fullmatch(value)
        or high_entropy(value)
    )


def credential_assignments(text: str) -> set[tuple[str, int]]:
    matches: set[tuple[str, int]] = set()
    for match in QUOTED_CREDENTIAL_ASSIGNMENT.finditer(text):
        value = next(
            value
            for value in (match.group("double"), match.group("single"), match.group("template"))
            if value is not None
        )
        if credential_literal(value):
            matches.add(("credential assignment", line_number(text, match.start())))
    return matches


def blocking_ip(match: re.Match[str]) -> bool:
    try:
        address = ipaddress.ip_address(match.group())
    except ValueError:
        return False
    return not local_ip(address) and not version_literal(match) and not css_pseudo_element(match)


def text_findings(text: str) -> set[tuple[str, int]]:
    matches: set[tuple[str, int]] = set()
    for category, pattern in (("IPv4 address", IPV4_CANDIDATE), ("IPv6 address", IPV6_CANDIDATE)):
        for match in pattern.finditer(text):
            if blocking_ip(match):
                matches.add((category, line_number(text, match.start())))

    for category, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            matches.add((category, line_number(text, match.start())))
    matches.update(credential_assignments(text))
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
    for match in reversed(list(QUOTED_CREDENTIAL_ASSIGNMENT.finditer(redacted))):
        value = next(
            value
            for value in (match.group("double"), match.group("single"), match.group("template"))
            if value is not None
        )
        if credential_literal(value):
            start = match.start() + match.group().find(value)
            redacted = redacted[:start] + "[REDACTED]" + redacted[start + len(value) :]
    return redacted
