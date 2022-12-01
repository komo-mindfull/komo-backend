from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import oAuth2

from ..database import get_db
from sqlalchemy.orm import Session
from .. import utils, models, oAuth2


router = APIRouter(tags=["Authentication"])


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

    if user_access_type == "customer":

        customer_query = db.query(models.Customer).filter(
            models.Customer.user_id == userData.id
        )
        check_customer_data = customer_query.first()

        if not check_customer_data:
            return {
                "access_token": token,
                "token_type": "bearer",
                "customer_registerd": False,
            }
        return {
            "access_token": token,
            "token_type": "bearer",
            "customer_registerd": True,
        }

    if user_access_type == "expert":

        expert_query = db.query(models.Expert).filter(
            models.Expert.user_id == userData.id
        )

        check_expert_data = expert_query.first()

        if not check_expert_data:
            return {
                "access_token": token,
                "token_type": "bearer",
                "expert_registerd": False,
            }

        return {
            "access_token": token,
            "token_type": "bearer",
            "expert_registerd": True,
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Not a valid user"
    )
