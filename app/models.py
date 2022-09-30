from flask_security import UsernameUtil
from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


# class Post(Base):
#     __tablename__ = 'posts'

#     id = Column(Integer, primary_key=True, nullable=False)
#     title = Column(String, nullable=False)
#     content = Column(String, nullable=False)
#     # user = Column(String, server_default='nice', nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True),
#                         server_default=text('now()'), nullable=False)
#     user_id = Column(Integer, ForeignKey(
#         "users.id", ondelete='CASCADE'), nullable=False)


# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True, nullable=False)
#     username = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     joined_at = Column(TIMESTAMP(timezone=True),
#                        server_default=text('now()'), nullable=False)


# class Votes(Base):
#     __tablename__ = 'votes'
#     user_id = Column(Integer, ForeignKey(
#         "users.id", ondelete='CASCADE'), primary_key=True, nullable=False)
#     post_id = Column(Integer, ForeignKey(
#         "posts.id", ondelete='CASCADE'), primary_key=True, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    joined_at = Column(TIMESTAMP(timezone=True),
                       server_default=text('now()'), nullable=False)
    email = Column(String, nullable=False, unique=True)
    utype = Column(String, nullable=False)


class Customer(Base):
    __tablename__ = 'customer'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)


class Expert(Base):
    __tablename__ = 'expert'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    prof = Column(String, nullable=False)
    yexp = Column(Integer, nullable=False, server_default='0')

    rating = Column(Integer, nullable=True)
    org = Column(String, nullable=False)
    proof = Column(String, nullable=True)

