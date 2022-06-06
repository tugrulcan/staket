def hash_password(password: str) -> str:
    """Hash a password for storing."""
    import binascii
    import hashlib
    import os

    salt = b"__hash__" + hashlib.sha256(os.urandom(60)).hexdigest().encode(
        "ascii"
    )
    pwdhash = hashlib.pbkdf2_hmac(
        hash_name="sha512",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=100000,
    )
    pwdhash = binascii.hexlify(data=pwdhash)
    return (salt + pwdhash).decode("ascii")


def is_hash(pw: str) -> bool:
    return pw.startswith("__hash__") and len(pw) == 200


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    import binascii
    import hashlib

    salt = stored_password[:72]
    stored_password = stored_password[72:]
    pwdhash: bytes = hashlib.pbkdf2_hmac(
        hash_name="sha512",
        password=provided_password.encode("utf-8"),
        salt=salt.encode("ascii"),
        iterations=100000,
    )
    return binascii.hexlify(pwdhash).decode("ascii") == stored_password
