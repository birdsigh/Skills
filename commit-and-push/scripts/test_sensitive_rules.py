#!/usr/bin/env python3
"""Checks for the sensitive-value rules. Run: python3 scripts/test_sensitive_rules.py"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

from sensitive_rules import redact, text_findings


def joined(*parts: str) -> str:
    """Assemble blocking fixtures at runtime so this file passes its own scanner."""
    return "".join(parts)


ALLOWED = (
    "localhost",
    "127.0.0.1",
    "127.0.0.53",
    "0.0.0.0",
    "::1",
    "::",
    "10.0.0.5",
    "172.16.4.9",
    "192.168.1.10",
    "169.254.10.2",
    "fe80::1",
    "fd00::5",
    "192.0.2.15",
    "198.51.100.7",
    "203.0.113.9",
    "2001:db8::8a2e",
    "v1.2.3.4",
    "version 1.2.3.4",
    "Chrome/124.0.0.0",
    "version: 1.2.3.4",
    "release 8.8.8.8",
    "package@1.2.3.4",
    "requests==1.2.3.4",
    "node>=8.8.8.8",
    "1.2.3.4-rc1",
    "1.2.3.4+build",
    joined("*", ":", ":before, *", ":", ":after"),
    joined("const apiKey = anth", "ropicKeyOrNull();"),
    joined("const secret = en", "v.MY_SECRET;"),
    joined("const token = proce", "ss.env.SECRET;"),
    joined("const token = awa", "it vault.get('token');"),
    joined("const headers = { 'x-api-key': api", "Key };"),
    joined("const headers = { 'x-api-key': this.deps.api", "Key };"),
    joined("const headers = { 'x-api-key': process.env.API", "_KEY };"),
    joined("const headers = { Authorization: options.to", "ken };"),
    joined("headers.set('Authorization', `Bearer ${to", "ken}`);"),
    joined("const apiKey = 'sk-ant-", "test';"),
    "function createClient(apiKey, token, secret) {}",
)
PUBLIC_V4 = joined("8.8", ".8.8")
BLOCKED = (
    PUBLIC_V4,
    f"https://{PUBLIC_V4}/",
    joined("1.1", ".1.1"),
    f"connect to {joined('51.15', '.200.7')} now",
    f"host={joined('203.0', '.114.9')}",
    joined("2606:4700:4700:", ":1111"),
    f"range {PUBLIC_V4}-{joined('8.8', '.8.9')}",
)
SECRETS = (
    joined("pass", "word: 'Abcdefghijklmnop0123456789+/='"),
    joined("-----BEGIN RSA ", "PRIVATE KEY-----"),
    joined("const apiKey = 'sk-ant-", "abcdefghijklmnopqrstuvwxyz0123456789';"),
    joined("headers.set('Authorization', 'Bearer gh", "p_real-looking-secret');"),
    joined("Authorization: 'Bearer Abcdefghijklmnop", "0123456789+/='"),
    joined("const config = { token: 'Abcdefghijkl", "mnop0123456789+/=' };"),
    joined("const url = 'https", "://user:password@example.com';"),
    joined("const jwt = 'eyJ", "hbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signaturevalue';"),
    joined("const github = 'gh", "p_abcdefghijklmnopqrstuvwxyz0123456789';"),
    joined("const google = 'AI", "zaabcdefghijklmnopqrstuvwxyz012345678';"),
    joined("const token = '0123456789abcdef", "0123456789abcdef01234567';"),
)


class SensitiveRules(unittest.TestCase):
    def test_browser_user_agent_versions_are_allowed_but_urls_are_not(self):
        self.assertEqual(text_findings("Chrome/124.0.0.0"), set())
        self.assertEqual(text_findings("chrome/124.0.0.0"), set())
        self.assertTrue(text_findings(PUBLIC_V4))
        self.assertTrue(text_findings(f"https://{PUBLIC_V4}/"))
        self.assertTrue(text_findings(joined("Product/8.8.8", ".8")))

    def test_allowed_values_are_not_flagged(self):
        for value in ALLOWED:
            with self.subTest(value=value):
                self.assertEqual(text_findings(value), set())
                self.assertEqual(redact(value), value)

    def test_routable_addresses_are_flagged(self):
        for value in BLOCKED:
            with self.subTest(value=value):
                self.assertTrue(text_findings(value))
                self.assertIn("[REDACTED]", redact(value))

    def test_secret_patterns_still_flagged(self):
        for value in SECRETS:
            with self.subTest(value=value):
                self.assertTrue(text_findings(value))
                self.assertIn("[REDACTED]", redact(value))

    def test_credential_assignment_is_redacted(self):
        value = joined("const config = { token: 'Abcdefghijkl", "mnop0123456789+/=' };")
        secret = joined("Abcdefghijkl", "mnop0123456789+/=")
        self.assertTrue(text_findings(value))
        self.assertNotIn(secret, redact(value))


if __name__ == "__main__":
    unittest.main()
