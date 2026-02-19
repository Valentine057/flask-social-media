from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import sqlite3

from .db import db


class User(db.Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
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
    caption = Column(String(2047))
    views = Column(Integer, nullable=False, default=0)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    user = relationship('User', back_populates='posts')
    
    def __init__(self, user_id, caption=None):
        self.caption = caption
        self.user_id = user_id

    def __str__(self):
        return f"<Post by {self.user.first_name}, on {self.created_at}>"
    
    
class Likes(db.Model):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    post_id = Column(ForeignKey('post.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "post_id"),
    )


    def __init__(self, user_id, post_id):
        self.user_id= user_id
        self.post_id= post_id




