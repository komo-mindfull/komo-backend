from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import oAuth2

from ..database import get_db
from sqlalchemy.orm import Session
from .. import utils, models, oAuth2


router = APIRouter(tags=["Authentication"])


def is_registered(usertype: str, db: Session, user_ID: int):
    user_exception = None
    if usertype == "customer":

        if (
            not db.query(models.Customer)
            .filter(models.Customer.user_id == user_ID)
            .first()
        ):
            return usertype, False, user_exception
        return usertype, True, user_exception

    if usertype == "expert":

        if (
            not db.query(models.Customer)
            .filter(models.Customer.user_id == user_ID)
            .first()
        ):
            return usertype, False, user_exception
        return usertype, True, user_exception

    user_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Cannot register user with utype '{usertype}'",
    )
    return usertype, False, user_exception


@router.post("/login")
def login(
    login_detail: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_query = db.query(models.User).filter(
        models.User.username == login_detail.username
    )

    userData = user_query.first()
    if not userData:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {login_detail.username} not found",
        )

    client_login_password = login_detail.password
    server_hashed_password = userData.password

    if utils.verify_password(client_login_password, server_hashed_password):
        token = oAuth2.create_acces_token(data={"id": userData.id})

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Password does not match"
        )

    user_access_type = userData.utype

    usertype, registered, user_exception = is_registered(
        user_access_type, db, userData.id
    )

    if user_exception:
        raise user_exception

    if not registered:
        return {
            "access_token": token,
            "token_type": "bearer",
            "cutomer_type": usertype,
            "customer_registerd": False,
        }
    return {
        "access_token": token,
        "token_type": "bearer",
        "cutomer_type": usertype,
        "customer_registerd": True,
    }

    # This is a test comment
