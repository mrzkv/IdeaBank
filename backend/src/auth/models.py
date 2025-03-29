from fastapi import HTTPException
from pydantic import BaseModel, field_validator
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
    role: str

    @field_validator("role", check_fields=False)
    def validate_role(cls, role):
        if role not in ["user", "expert"]:
            raise HTTPException(status_code=400, detail="Incorrect role")
        return role

class UserFIO(BaseModel):
    name: str
    surname: str
    patronymic: str