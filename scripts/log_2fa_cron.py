#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timezone

# ✅ Add app folder to Python path
sys.path.append("/app/app")

from scripts.totp_utils import generate_totp_code


SEED_PATH = "/data/seed.txt"

def main():
    if not os.path.exists(SEED_PATH):
        print("Seed not found")
        return

    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} - 2FA Code: {code}")

if __name__ == "_main_":
    main()