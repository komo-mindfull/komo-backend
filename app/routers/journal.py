from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db

from ..oAuth2 import get_current_user
from .. import models
from ..schemas import JournalEntry, CreatedJournal, AddLinks, AddLinksResponse
from typing import List

router = APIRouter(tags=["journal"])


# Route to create new journal
@router.post(
    "/journal", status_code=status.HTTP_201_CREATED, response_model=CreatedJournal
)
def create_entry(
    new_entry: JournalEntry,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):

    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )
    customer_data: models.Customer = customer_q.first()

    if customer_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    new_journal_entry = new_entry.dict()

    entry = models.Journal(**new_journal_entry, customer_id=customer_data.user_id)

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry

# Route to delete a journal entry
@router.delete("/journal/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Does not exist"
        )

    entry_q = db.query(models.Journal).filter(models.Journal.id == entry_id)
    entry_data = entry_q.first()

    if entry_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry does not exist"
        )

    if entry_data.customer_id != customer_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this entry",
        )

    db.delete(entry_data)
    db.commit()

    return "Entry deleted"


# Route to add links to a journal entry
@router.put("/journal/links/{entry_id}", status_code=status.HTTP_202_ACCEPTED, response_model=AddLinksResponse)
def new_journal_links(
    entry_id: int,
    parent_ID: AddLinks,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    """ 
    entery_ID  = Id of the child entry \n
    parent_ID = id of the parent entry
    """
    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )
    customer_data = customer_q.first()

    #Check if user exists
    if customer_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    entry_q = db.query(models.Journal).filter(models.Journal.id == entry_id)
    entry_data  = entry_q.first()

    # Check if entry exists
    if entry_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry does not exist"
        )

    # Check if user has permission to update entry
    if entry_data.customer_id != customer_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this entry",
        )

    journal_query = db.query(models.Journal).filter(models.Journal.id == parent_ID.parent_id, models.Journal.customer_id == customer_data.user_id)
    journal_data = journal_query.first()
    if journal_data is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to link parent_ID {} to this entry".format(parent_ID.parent_id)
        )
    # Check if link to parent entry exists

    if entry_data.link_ids:
        if parent_ID.parent_id in entry_data.link_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This entry is already linked to this parent",
            )
        entry_data.link_ids.append(parent_ID.parent_id)
        entry_q.update({"link_ids": entry_data.link_ids}, synchronize_session=False)

    
    else:
        list_ID = [parent_ID.parent_id]
        entry_q.update({"link_ids": list_ID}, synchronize_session=False)
    
    
    db.commit()
    db.refresh(entry_data)

    return entry_data


# Route to get all journal entries
@router.get(
    "/journal", status_code=status.HTTP_200_OK, response_model=List[CreatedJournal]
)
def get_all_entries(
    db: Session = Depends(get_db), current_user: int = Depends(get_current_user)
):
    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    entries = (
        db.query(models.Journal)
        .filter(models.Journal.customer_id == customer_data.user_id)
        .order_by(models.Journal.date_created)
        .all()
    )

    return entries

# Route to update a journal entry
# @router.put(
#     "/journal/{entry_id}",
#     status_code=status.HTTP_202_ACCEPTED,
#     response_model=CreatedJournal,
# )
# def update_journal(
#     entry_id: int,
#     updated_entry: JournalEntry,
#     db: Session = Depends(get_db),
#     current_user: int = Depends(get_current_user),
# ):
#     customer_q = db.query(models.Customer).filter(
#         models.Customer.user_id == current_user
#     )
#     customer_data = customer_q.first()

#     if customer_data is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
#         )

#     entry_q = db.query(models.Journal).filter(models.Journal.id == entry_id)
#     entry_data = entry_q.first()

#     if entry_data is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Entry does not exist"
#         )

#     if entry_data.customer_id != customer_data.user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to update this entry",
#         )

#     keyarr = []
#     new_entry_data = updated_entry.dict()
#     for i in new_entry_data:
#         if new_entry_data[i] is None:
#             keyarr.append(i)
#     for i in keyarr:
#         new_entry_data.pop(i)

#     new_entry_data.update({"customer_id": customer_data.user_id})

#     entry_q.update(new_entry_data, synchronize_session=False)
#     db.commit()
#     db.refresh(entry_data)

#     return entry_data
