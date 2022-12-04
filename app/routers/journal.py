from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session

from ..services.journal import add_parent_links
from ..getJournalLinks import create_journal_graph
from ..database import get_db

from ..oAuth2 import get_current_user
from .. import models
from ..schemas import (
    GetALlJournalResponse,
    JournalEntry,
    CreatedJournal,
    AddLinks,
    AddLinksResponse,
)
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
    parent_ID = new_journal_entry["link_ids"]

    if parent_ID is not None:

        journal_query = db.query(models.Journal).filter(
            models.Journal.id == parent_ID,
            models.Journal.customer_id == customer_data.user_id,
        )

        journal_data = journal_query.first()
        if journal_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Authorized to link parent_ID {} to this entry".format(
                    parent_ID
                ),
            )
        new_journal_entry["link_ids"] = [parent_ID]

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
@router.put(
    "/journal/links/{entry_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AddLinksResponse,
)
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

    # Check if user exists
    if customer_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    journal_entry_data = add_parent_links(parent_ID, entry_id, customer_data, db)

    return journal_entry_data


# Route to get all journal entries
@router.get(
    "/journal", status_code=status.HTTP_200_OK, response_model=GetALlJournalResponse
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

    entries: list[models.Journal] = (
        db.query(models.Journal)
        .filter(models.Journal.customer_id == customer_data.user_id)
        .order_by(models.Journal.date_created)
        .all()
    )

    nodes, edges = create_journal_graph(entries)
    return {"data": entries, "nodes": nodes, "edges": edges}
