from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    utype: str

class CustomerProfile(BaseModel):
    name: str
    age: int
    gender: str

class CreatedCustomer(CustomerProfile):
    class Config:
        orm_mode = True

class CreatedUser(BaseModel):
    # Email validator can be used to validate emails.
    id: int
    username: str
    email: EmailStr
    joined_at: datetime

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: Optional[int] = None
