from flask_security import UsernameUtil
from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

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

class Journal(Base):
    __tablename__ = 'journal'

    id = Column(Integer, primary_key=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.user_id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    date_created = Column(TIMESTAMP(timezone=True), server_default = text('now()'), nullable=False)
    date_updated = Column(TIMESTAMP(timezone=True), server_default = text('now()'), nullable=False)
    user_mood = Column(String, nullable=False, server_default='neutral')


