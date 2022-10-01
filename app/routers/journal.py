from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db

from ..oAuth2 import get_current_user
from .. import models
from ..schemas import JournalEntry, CreatedJournal
from typing import List
from ..sentiment import sentiment_pipeline

router = APIRouter(
    tags=['journal']
)

def analyze_sentiment(text: str):
    data = sentiment_pipeline(text)
    return data[0]['label']

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
        
        else:
            mood = analyze_sentiment(new_journal_entry['body'])
    
    new_journal_entry['customer_id'] = customer_data.user_id
    new_journal_entry['user_mood'] = mood

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    entries = db.query(models.Journal).filter(models.Journal.customer_id == customer_data.user_id).order_by(models.Journal.date_created).all()

    return entries

# Route to delete a journal entry
@router.delete("/journal/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id : int, db : Session = Depends(get_db), current_user : int = Depends(get_current_user)):
    customer_q = db.query(models.Customer).filter(models.Customer.user_id == current_user)
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Does not exist")

    entry_q = db.query(models.Journal).filter(models.Journal.id == entry_id)
    entry_data = entry_q.first()

    if entry_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry does not exist")

    if entry_data.customer_id != customer_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this entry")

    db.delete(entry_data)
    db.commit()

    return "Entry deleted"

# Route to update a journal entry
@router.put("/journal/{entry_id}", status_code=status.HTTP_202_ACCEPTED, response_model=CreatedJournal)
def update_journal(entry_id : int, updated_entry : JournalEntry, db : Session = Depends(get_db), current_user : int = Depends(get_current_user)):
    customer_q = db.query(models.Customer).filter(models.Customer.user_id == current_user)
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    entry_q = db.query(models.Journal).filter(models.Journal.id == entry_id)
    entry_data = entry_q.first()

    if entry_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry does not exist")

    if entry_data.customer_id != customer_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this entry")
    

    keyarr = []
    new_entry_data = updated_entry.dict()

    if new_entry_data['body'] is not None:
        mood = analyze_sentiment(new_entry_data['body'])
    else:
        mood = entry_data.user_mood
    for i in new_entry_data:
        if new_entry_data[i] is None:
            keyarr.append(i)
    for i in keyarr:
        new_entry_data.pop(i)

    new_entry_data.update({'customer_id': customer_data.user_id})
    
    new_entry_data.update({'user_mood': mood})
    
    entry_q.update(new_entry_data, synchronize_session=False)
    db.commit()
    db.refresh(entry_data)

    return entry_data
#nice