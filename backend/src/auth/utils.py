from argon2 import PasswordHasher

ph = PasswordHasher()

async def verify_password(password, hashed_password) -> bool:
    return ph.verify(password=password, hash=hashed_password)
