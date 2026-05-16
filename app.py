from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
from pathlib import Path
import time

# crypto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.backends import default_backend

# totp
import pyotp

DATA_SEED_PATH = Path("/data/seed.txt")
PRIVATE_KEY_PATH = Path("student_private.pem")

app = FastAPI(title="TOTP assignment API")


# ---------- Models ----------
class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# ---------- Helpers ----------
def load_private_key(path: Path, password: bytes | None = None) -> RSAPrivateKey:
    if not path.exists():
        raise FileNotFoundError(f"Private key not found at {path}")

    data = path.read_bytes()

    return serialization.load_pem_private_key(
        data,
        password=password,
        backend=default_backend()
    )


def decrypt_seed_base64(encrypted_seed_b64: str, private_key: RSAPrivateKey) -> str:
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64, validate=True)
    except Exception:
        raise ValueError("Invalid base64 encrypted_seed")

    try:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise ValueError("RSA decryption failed")

    try:
        seed = plaintext.decode("utf-8").strip()
    except Exception:
        raise ValueError("Decrypted data not valid UTF-8")

    # validate seed
    if len(seed) != 64 or any(c not in "0123456789abcdefABCDEF" for c in seed):
        raise ValueError("Invalid seed format")

    return seed.lower()


def write_seed_file(hex_seed: str):
    DATA_SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_SEED_PATH.write_text(hex_seed, encoding="utf-8")


def read_seed_file() -> str:
    if not DATA_SEED_PATH.exists():
        raise FileNotFoundError("Seed not decrypted yet")

    seed = DATA_SEED_PATH.read_text(encoding="utf-8").strip()

    if len(seed) != 64:
        raise ValueError("Seed file malformed")

    return seed


def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode().rstrip("=")


def generate_totp_and_remaining(hex_seed: str):
    b32 = hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        b32,
        digits=6,
        interval=30
    )

    code = totp.now()

    current_time = int(time.time())
    valid_for = 30 - (current_time % 30)

    return code, valid_for


def verify_totp(hex_seed: str, code: str, window: int = 1) -> bool:
    b32 = hex_to_base32(hex_seed)

    totp = pyotp.TOTP(
        b32,
        digits=6,
        interval=30
    )

    return totp.verify(code, valid_window=window)


# ---------- Routes ----------

@app.post("/decrypt-seed")
async def decrypt_seed(req: DecryptRequest):

    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)

        hex_seed = decrypt_seed_base64(
            req.encrypted_seed,
            private_key
        )

        write_seed_file(hex_seed)

        return {"status": "ok"}

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"}
        )


@app.get("/generate-2fa")
async def generate_2fa():

    try:
        hex_seed = read_seed_file()

        code, valid_for = generate_totp_and_remaining(hex_seed)

        return {
            "code": code,
            "valid_for": valid_for
        }

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"}
        )


@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):

    if not req.code or req.code.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"}
        )

    try:
        hex_seed = read_seed_file()

        valid = verify_totp(
            hex_seed,
            req.code.strip(),
            window=1
        )

        return {"valid": bool(valid)}

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"}
        )