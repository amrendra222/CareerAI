import hashlib
import hmac
import secrets


ITERATIONS = 310000


def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    return (
        f"pbkdf2_sha256$"
        f"{ITERATIONS}$"
        f"{salt.hex()}$"
        f"{password_hash.hex()}"
    )


def verify_password(
    password: str,
    stored_hash: str
) -> bool:

    try:

        algorithm, iterations, salt_hex, hash_hex = (
            stored_hash.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations)
        )

        return hmac.compare_digest(
            password_hash.hex(),
            hash_hex
        )

    except Exception:

        return False


def create_token() -> str:

    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()