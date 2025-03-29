from argon2 import PasswordHasher
from backend.src.auth.models import UserFIO
from random import randint, choice
import string
ph = PasswordHasher()

async def verify_password(password, hashed_password) -> bool:
    return ph.verify(password=password, hash=hashed_password)

async def hash_password(password):
    return ph.hash(password=password)


async def generate_password(length=12):

    letters = string.ascii_letters
    digits = string.digits
    specials = "!@#$%^&:\"'\\>?<*()-_=+"
    all_chars = letters + digits + specials

    password = "".join(choice(all_chars) for _ in range(length))
    return password

async def generate_login(fio: UserFIO):
    name = await transliterate(fio.name)
    surname = await transliterate(fio.surname)
    patronymic = await transliterate(fio.patronymic)
    if randint(0, 1) == 1:
        return f"{name}_{surname}_{patronymic}"
    else:
        return f"{name}{surname}{patronymic}"

# Соответствует -> ГОСТ 7.79-2000
async def transliterate(text):
    mapping = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    return ''.join(mapping.get(c, c) for c in text)