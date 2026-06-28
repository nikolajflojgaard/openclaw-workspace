#!/usr/bin/env python3
"""Resolve a Home Assistant API bearer token for unattended local jobs."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import textwrap


SERVICE_NAME = "homeassistant-mcp-token"
SSH_HOST = os.environ.get("HOMEASSISTANT_SSH_HOST", "homeassistant")


def _run(cmd: list[str], **kwargs) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, **kwargs).strip()


def _token_from_env() -> str | None:
    token = os.environ.get("HOMEASSISTANT_MCP_TOKEN", "").strip()
    return token or None


def _token_from_keychain() -> str | None:
    try:
        user = _run(["whoami"])
        token = _run(["security", "find-generic-password", "-a", user, "-s", SERVICE_NAME, "-w"])
    except subprocess.CalledProcessError:
        return None
    if not token or "\n" in token or token.startswith("keychain:"):
        return None
    return token


def _token_from_homeassistant_ssh() -> str | None:
    remote_python = r"""
import base64
import hashlib
import hmac
import json
from pathlib import Path
import time


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


data = json.loads(Path("/config/.storage/auth").read_text()).get("data", {})
tokens = data.get("refresh_tokens", [])
preferred_names = ("Jason", "ClawNew")
refresh_token = None
for name in preferred_names:
    refresh_token = next(
        (
            item
            for item in tokens
            if item.get("client_name") == name
            and item.get("token_type") == "long_lived_access_token"
        ),
        None,
    )
    if refresh_token:
        break
if refresh_token is None:
    refresh_token = next(
        (
            item
            for item in tokens
            if item.get("token_type") == "long_lived_access_token"
        ),
        None,
    )
if refresh_token is None:
    raise SystemExit("No long-lived Home Assistant token record found")

now = int(time.time())
exp = now + int(float(refresh_token.get("access_token_expiration") or 315360000))
header = {"alg": "HS256", "typ": "JWT"}
payload = {"iss": refresh_token["id"], "iat": now, "exp": exp}
signing_input = (
    b64url(json.dumps(header, separators=(",", ":")).encode())
    + "."
    + b64url(json.dumps(payload, separators=(",", ":")).encode())
).encode()
signature = hmac.new(refresh_token["jwt_key"].encode(), signing_input, hashlib.sha256).digest()
print(signing_input.decode() + "." + b64url(signature))
"""
    command = "sudo -n python3 - <<'PY'\n" + remote_python.strip() + "\nPY"
    try:
        token = _run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=10",
                SSH_HOST,
                command,
            ]
        )
    except subprocess.CalledProcessError:
        return None
    if token.count(".") != 2:
        return None
    return token


def get_token() -> str:
    for resolver in (_token_from_env, _token_from_keychain, _token_from_homeassistant_ssh):
        token = resolver()
        if token:
            return token
    raise RuntimeError(
        textwrap.dedent(
            """
            Unable to resolve Home Assistant token.
            Tried HOMEASSISTANT_MCP_TOKEN, macOS Keychain, and SSH minting from Home Assistant auth storage.
            """
        ).strip()
    )


if __name__ == "__main__":
    print(get_token())
