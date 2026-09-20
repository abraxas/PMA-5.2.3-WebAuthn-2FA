# Vendor report — phpMyAdmin 5.2.3 WebAuthn 2FA bypass

**To:** security@phpmyadmin.net  
**PGP:** DA68AB39218AB947  
**From:** Abraxas Labs — https://abraxaslabs.tech

Do not post this as a public GitHub issue until phpMyAdmin publishes a PMASA.

---

## Title

phpMyAdmin 5.2.3 CustomServer skips WebAuthn assertion signature — 2FA bypass after password

## Affected website or repository

https://github.com/phpmyadmin/phpmyadmin  
Tag **RELEASE_5_2_3** (5.2.3). Default tarball / `composer install --no-dev` (no `web-auth/webauthn-lib`).

## Vulnerability Type

CWE-347 (Improper Verification of Cryptographic Signature), CWE-287 (Improper Authentication)  
**High** CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (8.1)  
**Remote**, after the victim MySQL password (or cookie login). Not unauthenticated OS RCE.

## Details

`Plugins\TwoFactor\WebAuthn::createServer()` uses `CustomServer` when `Webauthn\Server` is absent. That is the default shipped tree (`web-auth/webauthn-lib` is suggest / require-dev only).

`CustomServer::parseAndValidateAssertionResponse` (libraries/classes/WebAuthn/CustomServer.php) checks:

- credential id is in `allowCredentials`
- `clientData.type == webauthn.get`
- challenge matches the session
- origin host matches the request host
- `rpIdHash` is SHA-256 of the host
- user-present flag is set

It **never** verifies `response.signature` with the enrolled public key. `CustomServerTest::testParseAndValidateAssertionResponse` accepts an assertion **with no public key**.

## Impact of Vulnerability

An attacker who already has the MySQL password (phishing, reuse, shared hosting panel, stolen cookie login) can complete WebAuthn 2FA **without the hardware key** and obtain a full phpMyAdmin session (SQL, users, export). 2FA as deployed on default 5.2.3 does not bind to the authenticator.

If `web-auth/webauthn-lib` is installed, `WebauthnLibServer` is used and this bypass does not apply.

## Reproduction or POC details

Loopback lab only. Witness `PMA-WEBAUTHN-BYPASS`.

```
cd lab
git clone --depth 1 --branch RELEASE_5_2_3 https://github.com/phpmyadmin/phpmyadmin.git src
docker compose up --build -d
python3 ../PMA-5.2.3-WebAuthn-2FA-Abraxas-Labs.py http://127.0.0.1:18080
```

Expected:

```
IOC password-login status=200 webauthn=True
SUCCESS PMA-WEBAUTHN-BYPASS WebAuthn 2FA accepted with garbage signature
```

The PoC POSTs `webauthn_request_response` with signature `not-a-real-signature-PMA-WEBAUTHN-BYPASS`.

## Fix

Verify `authenticatorData || SHA-256(clientDataJSON)` with the stored COSE public key; bind `userHandle`; enforce `signCount`. Make `web-auth/webauthn-lib` a real dependency and delete `CustomServer`, or fail closed if the library is missing.
