from fastapi import HTTPException, status, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from ..oAuth2 import get_current_user
from .. import models
from ..schemas import CustomerProfile, CreatedCustomer, UpdateCustomerProfile


router = APIRouter(tags=["Customer"])
# Route to create a customer profile
# TODO Make sure only correct user can create a profile
@router.post(
    "/users/customer",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedCustomer,
)
def create_customer(
    customerp: CustomerProfile,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )

    if customer_q.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer profile already exists",
        )

    custData = customerp.dict()
    custData["user_id"] = current_user
    data = models.Customer(**custData)
    db.add(data)
    db.commit()
    db.refresh(data)

    return data


# Route to get all customer profiles
@router.get(
    "/users/customer",
    status_code=status.HTTP_200_OK,
    response_model=list[CreatedCustomer],
)
def get_all_customers(db: Session = Depends(get_db)):
    customers = db.query(models.Customer).all()
    return customers


# Route to update a customer profile
@router.put(
    "/users/customer/update",
    status_code=status.HTTP_200_OK,
    response_model=CreatedCustomer,
)
def update_customer(
    update_cust: UpdateCustomerProfile,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):

    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )
    customer_data = customer_q.first()
    if not customer_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer profile not found"
        )
    new_cust_data = update_cust.dict()
    keyarr = []

    for i in new_cust_data:
        if new_cust_data[i] is None:
            keyarr.append(i)
    for i in keyarr:
        new_cust_data.pop(i)
    del keyarr

    new_cust_data.update({"user_id": current_user})

    customer_q.update(new_cust_data, synchronize_session=False)
    db.commit()
    db.refresh(customer_data)

    return customer_data
