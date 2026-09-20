Place phpMyAdmin 5.2.3 sources in `lab/src`:

https://github.com/phpmyadmin/phpmyadmin

```bash
git clone --depth 1 --branch RELEASE_5_2_3 https://github.com/phpmyadmin/phpmyadmin.git src
docker compose up --build -d
python3 ../PMA-5.2.3-WebAuthn-2FA-Abraxas-Labs.py http://127.0.0.1:18080
```

Witness: `SUCCESS PMA-WEBAUTHN-BYPASS`. Loopback only.
