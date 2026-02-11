from sqlalchemy import Column, Integer, String, Date, TIMESTAMP
from sqlalchemy.sql import func

from .db import DbTableBase


class User(DbTableBase):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    date_of_birth = Column(Date)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


    def __init__(self, first_name, last_name, email, password, date_of_birth=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.date_of_birth = date_of_birth
    
    def __str__(self):
        return f"<User {self.first_name} {self.last_name}>"
