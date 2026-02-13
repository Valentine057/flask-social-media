from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .db import db


class User(db.Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    date_of_birth = Column(Date)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    posts = relationship('Post', back_populates='user')

    def __init__(self, first_name, last_name, email, password, date_of_birth=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.date_of_birth = date_of_birth
    
    def __str__(self):
        return f"<User {self.first_name} {self.last_name}>"
    
    def __getitem__(self, name):
        return getattr(self, name)
    
    
class Post(db.Model):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)
    caption = Column(String)
    likes = Column(Integer, nullable=False, default=0)
    views = Column(Integer, nullable=False, default=0)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    user = relationship('User', back_populates='posts')
    
    def __init__(self, user_id, caption=None):
        self.caption = caption
        self.user_id = user_id

    def __str__(self):
        return f"<Post by {self.user.first_name}, {self.likes} likes>"

