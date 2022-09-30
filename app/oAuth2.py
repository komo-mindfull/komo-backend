from jose import JWTError, jwt
from datetime import timedelta, datetime

from app import models
from . import schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlalchemy.orm import Session
from . database import get_db
from . config import envar
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECERET_KEY = envar.secret_key
ALGORITHM = envar.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = envar.access_token_expire_minutes


def create_acces_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECERET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECERET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id) # fix pydantic model

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate the user", headers={"WWW-Authenticate":  "Bearer"})

    token_data = verify_token(
        token, credentials_exception)

    is_user = db.query(models.User).filter(
        models.User.id == token_data.id).first()
    if is_user is None:
        raise credentials_exception

    return is_user.id
