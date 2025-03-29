from pydantic import BaseModel
from typing import List

class LoginScheme(BaseModel):
    login: str
    password: str

class UserSchema(BaseModel):
    name: str
    surname: str
    patronymic: str
    password: str | None = None
    login: str | None = None

class UsersDataScheme(BaseModel):
    users_data: List[UserSchema]

class UserFIO(BaseModel):
    name: str
    surname: str
    patronymic: str