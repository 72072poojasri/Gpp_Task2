#!/usr/bin/env python3

import base64
from datetime import datetime, timezone
import pyotp

def main():
    seed_path = "/data/seed.txt"

    try:
        # 1. Read hex seed
        with open(seed_path, "r") as f:
            hex_seed = f.read().strip()

        # 2. Convert hex -> base32 (CORRECT WAY)
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode()

        # 3. Generate TOTP (SHA1, 30s, 6 digits default)
        totp = pyotp.TOTP(base32_seed)
        code = totp.now()

        # 4. UTC timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # 5. Output
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    main()
