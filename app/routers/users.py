from .. import models, utils
from ..schemas import CreatedCustomer, CustomerProfile, ExpertCreated, UpdateCustomerProfile, User, CreatedUser, ExpertProfile
from ..oAuth2 import get_current_user

from fastapi import status, HTTPException, Depends, Response, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

# TODO Add prefixes to path operations
router = APIRouter(
    tags=['Users']
)

# Route to create a new user
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

# Route to create a customer profile
@router.post("/users/customer", status_code=status.HTTP_201_CREATED, response_model=CreatedCustomer)
def create_customer(customerp: CustomerProfile, response: Response, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    custData = customerp.dict()
    custData['user_id'] = current_user
    data = models.Customer(**custData)
    db.add(data)
    db.commit()
    db.refresh(data)

    return data

# Route to update a customer profile
@router.put("/users/customer/update", status_code=status.HTTP_200_OK, response_model=CreatedCustomer)
def update_customer(update_cust: UpdateCustomerProfile, response: Response, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    # TODO Test case for this function
    # TODO User not logged in
    # TODO User is not a customer
    # TODO User is a customer
    # TODO incorrect data
    customer_q = db.query(models.Customer).filter(models.Customer.user_id == current_user)
    customer_data = customer_q.first()
    if not customer_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Customer profile not found")
    new_cust_data = update_cust.dict()
    keyarr = []

    for i in new_cust_data:
       if new_cust_data[i] is None:
           keyarr.append(i)
    for i in keyarr:
        new_cust_data.pop(i)
    del (keyarr)

    new_cust_data.update({'user_id': current_user})
    
    customer_q.update(new_cust_data, synchronize_session=False)
    db.commit()
    db.refresh(customer_data)

    return customer_data

    

@router.post("/users/expert", status_code=status.HTTP_201_CREATED, response_model=ExpertCreated)
def create_expert(expert_profile: ExpertProfile, response: Response, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    expertData = expert_profile.dict()
    print(expertData)
    expertData['user_id'] = current_user
    data = models.Expert(**expertData)
    db.add(data)
    db.commit()
    db.refresh(data)

    return data

