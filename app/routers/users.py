from .. import models, utils
from ..schemas import (
    CreatedCustomer,
    CreatedUserLogin,
    CustomerProfile,
    ExpertCreated,
    UpdateCustomerProfile,
    UpdateExpertProfile,
    User,
    CreatedUser,
    ExpertProfile,
)
from ..oAuth2 import get_current_user, create_acces_token


from fastapi import status, HTTPException, Depends, Response, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

# TODO Add prefixes to path operations
router = APIRouter(tags=["Users"])

# Route to create a new user
@router.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=CreatedUserLogin
)
def create_user(new_user: User, response: Response, db: Session = Depends(get_db)):

    # TODO Add verification using OTP

    create_user_q = db.query(models.User).filter(
        models.User.username == new_user.username
    )
    if create_user_q.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username {new_user.username} already exists",
        )

    userData = new_user.dict()
    userData["password"] = utils.hash_password(userData["password"])
    user_details = models.User(**userData)
    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    user_details = user_details.__dict__
    print(user_details)
    token = create_acces_token(data={"id": user_details["id"]})

    user_details["access_token"] = token
    user_details["token_type"] = "bearer"

    return user_details


# Route to get all users
@router.get("/users", status_code=status.HTTP_200_OK, response_model=list[CreatedUser])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


# Route to delete a user
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You are not authorized to delete this user",
        )
    user = db.query(models.User).filter(models.User.id == user_id)
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
