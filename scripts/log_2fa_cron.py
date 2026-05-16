#!/usr/bin/env python

import base64
from datetime import datetime, timezone
from pathlib import Path
import pyotp

SEED_PATH = Path("/data/seed.txt")


def generate_totp_code(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)

    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30
    )

    return totp.now()


def main():
    try:
        if not SEED_PATH.exists():
            print("ERROR: seed file not found")
            return

        hex_seed = SEED_PATH.read_text().strip()

        code = generate_totp_code(hex_seed)

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()