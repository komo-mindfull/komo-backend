from .. import models, utils
from ..schemas import CreatedCustomer, CustomerProfile, User, CreatedUser
from ..oAuth2 import get_current_user

from fastapi import status, HTTPException, Depends, Response, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

# TODO Add prefixes to path operations
router = APIRouter(
    tags=['Users']
)


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=CreatedUser)
def create_user(new_user: User, response: Response, db: Session = Depends(get_db)):

    create_user_q = db.query(models.User).filter(models.User.username == new_user.username)
    if create_user_q.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with username {new_user.username} already exists")

    userData = new_user.dict()
    userData['password'] = utils.hash_password(userData['password'])
    data = models.User(**userData)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data
    
@router.post("/users/customer", status_code=status.HTTP_201_CREATED, response_model=CreatedCustomer)
def create_customer(customerp: CustomerProfile, response: Response, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    custData = customerp.dict()
    custData['user_id'] = current_user
    data = models.Customer(**custData)
    db.add(data)
    db.commit()
    db.refresh(data)

    return data

@router.post("/user/expert", status_code=status.HTTP_201_CREATED, response_model=CreatedCustomer)
def create_expert():
    pass

