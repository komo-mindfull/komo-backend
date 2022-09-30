from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db

from ..oAuth2 import get_current_user
from .. import models
from ..schemas import JournalEntry, CreatedJournal
from typing import List

router = APIRouter(
    tags=['journal']
)


# Route to create new journal
@router.post("/journal", status_code=status.HTTP_201_CREATED, response_model=CreatedJournal)
def create_entry(new_entry : JournalEntry, db : Session = Depends(get_db), current_user : int = Depends(get_current_user)):
    
    customer_q = db.query(models.Customer).filter(models.Customer.user_id == current_user)
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does exist")
    
    new_journal_entry = new_entry.dict()
    if new_journal_entry['title'] is None:
        if new_journal_entry['body'] is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and body cannot be empty")
        new_journal_entry['title'] = 'Untitled'
    else:
        if new_journal_entry['body'] is None:
            new_journal_entry['body'] = 'No description'
    
    new_journal_entry['customer_id'] = customer_data.user_id

    entry = models.Journal(**new_journal_entry)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry

# Route to get all journal entries
@router.get("/journal", status_code=status.HTTP_200_OK, response_model=List[CreatedJournal])
def get_all_entries(db : Session = Depends(get_db), current_user : int = Depends(get_current_user)):
    customer_q = db.query(models.Customer).filter(models.Customer.user_id == current_user)
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does exist")

    entries = db.query(models.Journal).filter(models.Journal.customer_id == customer_data.user_id).order_by(models.Journal.date_created).all()

    return entries