from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, UniqueConstraint, Table, text, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy_views import CreateView

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


class View(Table):
    is_view = True


class MyCustomCreateView(CreateView):
    def __init__(self, view):
        super().__init__(view.__view__, view.__definition__)


class FullPostWithLikes:
    __view__ = View(
        'full_post_with_likes', MetaData(),
        Column('id', Integer, primary_key=True),
        Column('caption', String(2047)),
        Column('views', Integer, nullable=False, default=0),
        Column('user_id', ForeignKey('user.id'), nullable=False),
        Column('created_at', TIMESTAMP, nullable=False),
        Column('first_name', String(255), nullable=False),
        Column('last_name', String(255), nullable=False),
        Column('like_count', Integer)
    )

    __definition__ = text('''
        SELECT post.id, post.caption, post.views, post.user_id, post.created_at, user.first_name, user.last_name, IFNULL(anon_1.like_count, 0) AS like_count
        FROM post
        LEFT OUTER JOIN user ON post.user_id = user.id
        LEFT OUTER JOIN (
            SELECT COUNT(likes.id) AS like_count, likes.post_id AS post_id FROM likes GROUP BY likes.post_id
        ) AS anon_1 ON post.id = anon_1.post_id''')


# keeping track of your defined views makes things easier
views = [FullPostWithLikes]

