<p align="center">
  <img src="header.png" alt="Abraxas Labs — PMA-5.2.3-WebAuthn-2FA" width="100%">
</p>

<p align="center">
  <a href="https://abraxaslabs.tech"><strong>abraxaslabs.tech</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas">github.com/abraxas</a>
  &nbsp;·&nbsp;
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas/PMA-5.2.3-WebAuthn-2FA">PMA-5.2.3-WebAuthn-2FA</a>
</p>

# PMA-5.2.3-WebAuthn-2FA

**phpMyAdmin** `5.2.3` — phpMyAdmin

phpMyAdmin 5.2.3 (default tarball, without web-auth/webauthn-lib) does not verify the WebAuthn assertion signature during two-factor login. After a valid password, an attacker can POST a forged webauthn_request_response that matches the session challenge, origin host, rpIdHash, and user-present flag with an arbitrary signature and obtain a full phpMyAdmin session.

| | |
|---|---|
| ID | PMA-5.2.3-WebAuthn-2FA (CVE pending — private vendor report) |
| CWE | [CWE-347](https://cwe.mitre.org/data/definitions/347.html), [CWE-287](https://cwe.mitre.org/data/definitions/287.html) |
| CVSS | **High: 8.1** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` |
| Product | [phpMyAdmin](https://www.phpmyadmin.net/) |
| Affected | **5.2.3** default tarball (`web-auth/webauthn-lib` absent) |
| Patched | vendor patch — not yet assigned |
| Auth | MySQL password (then WebAuthn 2FA skipped) |
| License | [GNU Affero GPL v3.0](LICENSE) |
| Lab | `127.0.0.1` only · vendor/client disclosure pack, not a scanner |

---

## Advisory (from the source map)

CustomServer::parseAndValidateAssertionResponse checks credential id, challenge, origin host, rpIdHash, and user-present flag. It never COSE-verifies response.signature and never uses the stored credential public key. createServer() uses CustomServer when Webauthn\Server is absent (default tarball; web-auth/webauthn-lib is suggest/require-dev only).

---

## Entry

- **Method:** `POST`
- **Path:** `/index.php?route=/`
- **Router:** cookie login then TwoFactor::check -&gt; Plugins\TwoFactor\WebAuthn::check
- **Notes:** POST webauthn_request_response after password. Field is a JSON PublicKeyCredential. Signature may be garbage.

### Call chain

- `POST /index.php?route=/ pma_username pma_password token`
- `AuthenticationPlugin::checkTwoFactor`
- `TwoFactor::check -&gt; WebAuthn::check`
- `POST webauthn_request_response = forged assertion`
- `CustomServer::parseAndValidateAssertionResponse (no signature verify)`
- `$_SESSION['two_factor_check']=true`
- `normal phpMyAdmin UI (witness PMA-WEBAUTHN-BYPASS in SUCCESS line)`

### Lab preconditions

- phpMyAdmin 5.2.3 without composer package web-auth/webauthn-lib
- cookie auth
- pmadb pma__userconfig with 2fa backend WebAuthn for the MySQL user
- attacker knows the MySQL password (or cookie login) for that user

### Witness

stdout contains SUCCESS PMA-WEBAUTHN-BYPASS WebAuthn 2FA accepted with garbage signature; still_2fa=False landed=True

### Not success

- webauthn_request_response still in the HTML after the second POST
- WebauthnLibServer in use (web-auth/webauthn-lib installed)
- reverse shell or outbound connect
- unauthenticated access without the MySQL password

---

## Patch / remediation

**Do this first:** Apply the vendor patch for **phpMyAdmin**. See references.

**Verify after upgrade**

- Re-run `PMA-5.2.3-WebAuthn-2FA-Abraxas-Labs.py` against the patched build: the mapped witness must **not** appear.
- Confirm the vendor advisory / changeset in the deployed tree (see references).
- A WAF signature is delay, not a patch.

**If you cannot update immediately**

- Disable or isolate the affected component.
- Hunt for the witness condition on production (new privileged users, unexpected files, injected rows — whatever this CVE's map names).

---

## Reproduction (authorized lab)

Target **only** http://127.0.0.1:18080 . Do not point this script at the internet.

```bash
cd lab
git clone --depth 1 --branch RELEASE_5_2_3 https://github.com/phpmyadmin/phpmyadmin.git src
docker compose up --build -d
python3 ../PMA-5.2.3-WebAuthn-2FA-Abraxas-Labs.py http://127.0.0.1:18080
```

Success is stdout `SUCCESS PMA-WEBAUTHN-BYPASS` with `still_2fa=False landed=True`. Generic 200 HTML is not it.

---

## Lab images

Loopback stack used to reproduce. Official images unless a `Dockerfile` in this folder builds from source.

- [`lab/docker-compose.yml`](lab/docker-compose.yml)
- [`lab/Dockerfile`](lab/Dockerfile)
- [`lab/init.sql`](lab/init.sql)
- [`lab/config.inc.php`](lab/config.inc.php)
- [`lab/README.md`](lab/README.md)

```bash
cd lab
docker compose up --force-recreate
```

Bind the vulnerable product tree next to Compose if the YAML mounts a local directory (plugin zip / source tag from the version table). Publish nothing except `127.0.0.1`.

---

## References

- [phpMyAdmin security](https://www.phpmyadmin.net/security/)
- [github.com/phpmyadmin/phpmyadmin](https://github.com/phpmyadmin/phpmyadmin) tag RELEASE_5_2_3
- [www.phpmyadmin.net/security/](https://www.phpmyadmin.net/security/)

- Abraxas Labs: [abraxaslabs.tech](https://abraxaslabs.tech) · [github.com/abraxas](https://github.com/abraxas) · [@abraxas_null](https://x.com/abraxas_null)

---

## Records (structured)

```
# phpMyAdmin 5.2.3 WebAuthn 2FA bypass

CWE: CWE-347, CWE-287

CVSS 3.1: High 8.1 `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`

PR:L because the MySQL password (or equivalent cookie login) is required. Not unauthenticated.

## NVD description

phpMyAdmin 5.2.3 (default tarball, without web-auth/webauthn-lib) does not verify the WebAuthn assertion signature during two-factor login. After a valid password, an attacker can POST a forged `webauthn_request_response` that matches the session challenge, origin host, rpIdHash, and user-present flag with an arbitrary signature and obtain a full phpMyAdmin session.

## Source

- libraries/classes/WebAuthn/CustomServer.php parseAndValidateAssertionResponse
- libraries/classes/Plugins/TwoFactor/WebAuthn.php createServer / check
- test/classes/WebAuthn/CustomServerTest.php testParseAndValidateAssertionResponse accepts an assertion with no public key

## Lab

Loopback http://127.0.0.1:18080 only. Witness PMA-WEBAUTHN-BYPASS.

File privately to security@phpmyadmin.net (PGP DA68AB39218AB947) before public disclosure.
```

---

## License

This disclosure pack is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE).

---

## Disclaimer

This pack is for **the vendor, the site owner, and licensed labs**. The script talks to `127.0.0.1`. Using it against systems you do not own is not authorized by Abraxas Labs. No warranty.

<p align="center">
  <a href="https://abraxaslabs.tech">abraxaslabs.tech</a> ·
  <a href="https://github.com/abraxas">github.com/abraxas</a> ·
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
</p>
