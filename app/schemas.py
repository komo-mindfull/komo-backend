from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    utype: str


class CreatedUser(BaseModel):
    # Email validator can be used to validate emails.
    id: int
    username: str
    email: EmailStr
    joined_at: datetime

    class Config:
        orm_mode = True


class CreatedUserLogin(CreatedUser):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class CustomerProfile(BaseModel):
    name: str
    age: int
    gender: str


class UpdateCustomerProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class CreatedCustomer(CustomerProfile):
    class Config:
        orm_mode = True


class ExpertProfile(BaseModel):
    name: str
    prof: str
    yexp: Optional[int]
    org: str


class UpdateExpertProfile(BaseModel):
    name: Optional[str]
    prof: Optional[str]
    yexp: Optional[int]
    org: Optional[str]


class ExpertCreated(ExpertProfile):
    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: Optional[int] = None


class JournalEntry(BaseModel):
    title: str
    body: str


class CreatedJournal(JournalEntry):
    id: int
    date_created: datetime

    class Config:
        orm_mode = True
