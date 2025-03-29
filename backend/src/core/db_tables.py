from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()




class Ideas(Base):
    __tablename__ = 'ideas'

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    name = Column(String)
    description = Column(Text)
    status = Column(String)
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)
    creator_id = Column(BigInteger)
    expert_id = Column(BigInteger)
    solution = Column(String)
    solution_description = Column(Text)


class Users(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    login = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    status = Column(String)

class UsersFio(Base):
    __tablename__ = 'users_fio'

    user_id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(String)
    surname = Column(String)
    patronymic = Column(String)
