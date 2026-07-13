#!/usr/bin/env python3
"""ProtoLab client: pair, deploy, remove, manage labs. Stdlib only (3.8+).

Exit codes: 0 ok, 1 error, 2 usage, 3 ambiguous/missing lab (ask the user),
4 auth failure (token revoked -- re-pair).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

try:
    import tomllib  # 3.11+
except ModuleNotFoundError:
    tomllib = None  # fall back to the minimal parser below

HOME_CONFIG = Path(os.environ.get("PROTOLAB_CONFIG", "~/.config/protolab/config")).expanduser()
LOCAL_CONFIG = Path(".protolab")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
RESERVED = {"settings", "api", "favicon.ico", "robots.txt"}
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
MAX_ZIP_BYTES = 25 * 1024 * 1024
MAX_ENTRIES = 500
SKIP_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".protolab"}
POLL_INTERVAL_S = 2
POLL_TIMEOUT_S = 330


def fail(msg: str, code: int = 1) -> "None":
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- config

def config_path() -> Path | None:
    if HOME_CONFIG.exists():
        return HOME_CONFIG
    if LOCAL_CONFIG.exists():
        return LOCAL_CONFIG
    return None


def _parse_simple_toml(text: str) -> dict:
    """Minimal TOML for this config's flat shape (pre-3.11 fallback).
    Handles quoted string values and [dotted.section] headers only."""
    data: dict = {}
    section = data
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = data
            for part in line[1:-1].strip().split("."):
                section = section.setdefault(part, {})
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                v = v[1:-1]
            section[k.strip()] = v
    return data


def load_config() -> "tuple[dict, Path | None]":
    path = config_path()
    if path is None:
        return {"labs": {}}, None
    text = path.read_text(encoding="utf-8")
    cfg = tomllib.loads(text) if tomllib else _parse_simple_toml(text)
    cfg.setdefault("labs", {})
    return cfg, path


def save_config(cfg: dict, path: Path) -> None:
    lines = []
    if cfg.get("default"):
        lines.append(f'default = "{cfg["default"]}"')
    for name, lab in cfg.get("labs", {}).items():
        lines.append("")
        lines.append(f"[labs.{name}]")
        lines.append(f'url = "{lab["url"]}"')
        lines.append(f'token = "{lab["token"]}"')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(0o600)


def resolve_lab(args) -> tuple[str, str, str]:
    """Resolution order per the ProtoLab spec. Returns (name, url, token)."""
    env_url, env_token = os.environ.get("PROTOLAB_URL"), os.environ.get("PROTOLAB_TOKEN")
    if env_url and env_token:
        return ("env-override", env_url.rstrip("/"), env_token)

    cfg, _ = load_config()
    labs = cfg["labs"]

    def pick(name: str, source: str) -> tuple[str, str, str]:
        lab = labs.get(name)
        if not lab:
            fail(f"lab '{name}' ({source}) not found; configured: {', '.join(labs) or 'none'}", 3)
        return (name, lab["url"].rstrip("/"), lab["token"])

    if os.environ.get("PROTOLAB_LAB"):
        return pick(os.environ["PROTOLAB_LAB"], "from PROTOLAB_LAB")
    if getattr(args, "lab", None):
        return pick(args.lab, "from --lab")
    if cfg.get("default") and cfg["default"] in labs:
        return pick(cfg["default"], "default")
    if len(labs) == 1:
        name = next(iter(labs))
        return pick(name, "only lab")
    if not labs:
        fail("no labs configured -- run: protolab.py pair --url <lab-url>", 3)
    fail(f"multiple labs and no default: {', '.join(labs)} -- pass --lab <name>", 3)
    raise AssertionError  # unreachable


# ---------------------------------------------------------------- http

def http(method: str, url: str, body: bytes | None = None,
         headers: dict | None = None) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            raw = res.read()
            status = res.status
    except urllib.error.HTTPError as e:
        raw = e.read()
        status = e.code
    except urllib.error.URLError as e:
        fail(f"cannot reach {url}: {e.reason}")
    try:
        return status, json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return status, raw.decode("utf-8", "replace")


def api_error(data) -> str:
    return data.get("error", str(data)) if isinstance(data, dict) else str(data)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------- verbs

def cmd_labs(_args) -> None:
    cfg, path = load_config()
    if not cfg["labs"]:
        print("No labs configured. Pair one with: protolab.py pair --url <lab-url>")
        return
    print(f"config: {path}")
    for name, lab in cfg["labs"].items():
        marker = " (default)" if cfg.get("default") == name else ""
        print(f"  {name}: {lab['url']}{marker}")


def cmd_status(args) -> None:
    cmd_labs(args)
    cfg, _ = load_config()
    if cfg["labs"] or (os.environ.get("PROTOLAB_URL") and os.environ.get("PROTOLAB_TOKEN")):
        cmd_health(args)


def cmd_health(args) -> None:
    name, url, token = resolve_lab(args)
    status, data = http("GET", f"{url}/api/health", headers=auth_headers(token))
    if status == 401:
        fail(f"token for '{name}' was revoked or invalid -- re-pair with: "
             f"protolab.py pair --url {url}", 4)
    if status != 200:
        fail(f"health check failed ({status}): {api_error(data)}")
    print(f"ok: '{name}' -> {data.get('base_url', url)} (lab: {data.get('lab_name', '?')})")


def derive_name(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or "lab"
    parts = host.split(".")
    candidate = parts[-2] if len(parts) >= 2 else parts[0]
    candidate = re.sub(r"[^a-z0-9_-]", "-", candidate.lower()).strip("-") or "lab"
    return candidate


def cmd_pair(args) -> None:
    url = args.url.rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url

    status, data = http("POST", f"{url}/api/pair",
                        body=json.dumps({"requester": socket.gethostname()}).encode(),
                        headers={"Content-Type": "application/json"})
    if status == 429:
        fail("rate limited -- the lab throttles pairing; wait a minute and retry")
    if status != 200:
        fail(f"pairing request failed ({status}): {api_error(data)}")
    code = data["code"]

    print(f"Pairing code: {code}")
    print(f"Open {url}/settings and approve code {code} (expires in ~5 minutes).")
    print("Waiting for approval...", flush=True)

    token = None
    deadline = time.monotonic() + POLL_TIMEOUT_S
    while time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_S)
        status, data = http("GET", f"{url}/api/pair/{code}")
        if status == 200:
            token = data["token"]
            break
        if status == 202:
            continue
        if status == 410:
            fail("pairing expired or was denied -- run pair again")
        if status == 429:
            time.sleep(10)
            continue
        fail(f"unexpected response while polling ({status}): {api_error(data)}")
    if token is None:
        fail("timed out waiting for approval -- run pair again")

    cfg, path = load_config()
    if args.local:
        path = LOCAL_CONFIG
    elif path is None:
        path = HOME_CONFIG

    # Dedupe by URL: re-pairing an existing lab updates it, never duplicates.
    existing = next((n for n, lab in cfg["labs"].items() if lab["url"].rstrip("/") == url), None)
    name = args.name or existing or derive_name(url)
    if not NAME_RE.match(name):
        fail(f"lab alias '{name}' must be lowercase alphanumeric/hyphen/underscore")
    if existing and args.name and args.name != existing:
        del cfg["labs"][existing]
        if cfg.get("default") == existing:
            cfg["default"] = name
    if name in cfg["labs"] and cfg["labs"][name]["url"].rstrip("/") != url and not existing:
        fail(f"alias '{name}' already points at {cfg['labs'][name]['url']} -- pass --name")

    first = not cfg["labs"]
    cfg["labs"][name] = {"url": url, "token": token}
    if first or not cfg.get("default"):
        cfg["default"] = name
    save_config(cfg, path)
    updated = "updated" if existing else "paired"
    print(f"{updated}: '{name}' -> {url} (config: {path}"
          f"{', now the default' if cfg['default'] == name else ''})")


def sanitize_slug(raw: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", raw.lower()).strip("-")[:63]
    return slug


def validate_slug(slug: str) -> None:
    if not SLUG_RE.match(slug):
        fail(f"invalid slug '{slug}': lowercase alphanumeric plus hyphens, 1-63 chars")
    if slug in RESERVED or slug.startswith("_"):
        fail(f"slug '{slug}' is reserved")


def zip_folder(folder: Path) -> bytes:
    if not (folder / "index.html").exists():
        fail(f"{folder} has no index.html at its root -- ProtoLab requires one")
    buf = io.BytesIO()
    count = 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(folder.rglob("*")):
            if not p.is_file() or p.name in SKIP_FILES:
                continue
            count += 1
            if count > MAX_ENTRIES:
                fail(f"more than {MAX_ENTRIES} files -- ProtoLab rejects this")
            zf.write(p, p.relative_to(folder).as_posix())
    data = buf.getvalue()
    if len(data) > MAX_ZIP_BYTES:
        fail(f"zip is {len(data)} bytes; ProtoLab's cap is {MAX_ZIP_BYTES}")
    if count == 0:
        fail(f"{folder} has no files to deploy")
    return data


def cmd_deploy(args) -> None:
    path = Path(args.path)
    if not path.exists():
        fail(f"{path} does not exist")

    if path.is_dir():
        slug = args.slug or sanitize_slug(path.resolve().name)
        body, ctype = zip_folder(path), "application/zip"
    elif path.suffix.lower() in (".html", ".htm"):
        slug = args.slug or sanitize_slug(path.stem)
        body, ctype = path.read_bytes(), "text/html"
    else:
        fail(f"{path} is neither a folder nor an .html file")
    validate_slug(slug)

    name, url, token = resolve_lab(args)
    status, data = http("PUT", f"{url}/api/prototypes/{slug}", body=body,
                        headers={**auth_headers(token), "Content-Type": ctype})
    if status == 401:
        fail(f"token for '{name}' was revoked or invalid -- re-pair with: "
             f"protolab.py pair --url {url}", 4)
    if status != 200:
        fail(f"deploy failed ({status}): {api_error(data)}")
    print(f"Deployed: {data['url']} ({data['files']} file(s), {data['bytes']} bytes, lab: {name})")


def cmd_remove(args) -> None:
    validate_slug(args.slug)
    name, url, token = resolve_lab(args)
    status, data = http("DELETE", f"{url}/api/prototypes/{args.slug}",
                        headers=auth_headers(token))
    if status == 401:
        fail(f"token for '{name}' was revoked or invalid -- re-pair with: "
             f"protolab.py pair --url {url}", 4)
    if status == 404:
        fail(f"no prototype '{args.slug}' on '{name}'")
    if status != 200:
        fail(f"remove failed ({status}): {api_error(data)}")
    print(f"Removed '{args.slug}' from '{name}' ({url})")


def cmd_set_default(args) -> None:
    cfg, path = load_config()
    if path is None or args.name not in cfg["labs"]:
        fail(f"lab '{args.name}' not found; configured: {', '.join(cfg['labs']) or 'none'}", 3)
    cfg["default"] = args.name
    save_config(cfg, path)
    print(f"default lab is now '{args.name}'")


def cmd_remove_lab(args) -> None:
    cfg, path = load_config()
    if path is None or args.name not in cfg["labs"]:
        fail(f"lab '{args.name}' not found; configured: {', '.join(cfg['labs']) or 'none'}", 3)
    url = cfg["labs"][args.name]["url"]
    del cfg["labs"][args.name]
    if cfg.get("default") == args.name:
        cfg["default"] = next(iter(cfg["labs"]), None)
    save_config(cfg, path)
    print(f"removed '{args.name}' from local config. Note: this does NOT revoke "
          f"the token -- do that on {url}/settings if needed.")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(prog="protolab.py", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("labs")
    sub.add_parser("status")

    p = sub.add_parser("health")
    p.add_argument("--lab")

    p = sub.add_parser("pair")
    p.add_argument("--url", required=True)
    p.add_argument("--name")
    p.add_argument("--local", action="store_true",
                   help="write ./.protolab instead of ~/.config/protolab/config")

    p = sub.add_parser("deploy")
    p.add_argument("path")
    p.add_argument("--slug")
    p.add_argument("--lab")

    p = sub.add_parser("remove")
    p.add_argument("slug")
    p.add_argument("--lab")

    p = sub.add_parser("set-default")
    p.add_argument("name")

    p = sub.add_parser("remove-lab")
    p.add_argument("name")

    args = ap.parse_args()
    {
        "labs": cmd_labs,
        "status": cmd_status,
        "health": cmd_health,
        "pair": cmd_pair,
        "deploy": cmd_deploy,
        "remove": cmd_remove,
        "set-default": cmd_set_default,
        "remove-lab": cmd_remove_lab,
    }[args.cmd](args)


if __name__ == "__main__":
    main()