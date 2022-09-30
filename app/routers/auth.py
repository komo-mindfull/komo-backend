from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import oAuth2

from ..database import get_db
from sqlalchemy.orm import Session
from .. import utils, models, oAuth2


router = APIRouter(
    tags=['Authentication']
)


@router.get("/login")
def login(user_detail: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(
        models.User.username == user_detail.username)

    userData = user_query.first()
    if not userData:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with username {user_detail.username} not found")

    auth_passowrd = user_detail.password
    hashed_password = userData.password

    if utils.verify_password(auth_passowrd, hashed_password):

        token = oAuth2.create_acces_token(
            data={'id': userData.id})
        return {"access_token": token, 'token_type': 'bearer'}

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Password does not match")
