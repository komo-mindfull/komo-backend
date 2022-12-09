from fastapi import status, HTTPException, Depends, Response, APIRouter
from sqlalchemy.orm import Session

from ..services.journal import JournalService
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
        journal_validation = JournalService(
            current_user_ID=current_user, db=db, parent_ID=parent_ID
        )
        if journal_validation.check_acess_parent_entry():
            new_journal_entry["link_ids"] = [parent_ID]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent entry does not exist",
            )

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
    customer_q = db.query(models.Customer).filter(
        models.Customer.user_id == current_user
    )
    customer_data = customer_q.first()

    if customer_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    child_entry_query = db.query(models.Journal).filter(
        models.Journal.id == entry_id, models.Journal.customer_id == current_user
    )
    child_entry_data = child_entry_query.first()

    if not child_entry_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User does not have access to requested journal with id {entry_id}",
        )

    journal_validation = JournalService(
        parent_ID=parent_ID.parent_id,
        child_ID=entry_id,
        current_user_ID=current_user,
        db=db,
    )

    # Checking if user has access to parent journal
    if not journal_validation.check_acess_parent_entry():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Either journal with id {parent_ID.parent_id} does not exist or user does not have access to it",
        )

    # Adding links using journal_validation object, returns query object
    child_entry_query = journal_validation.connect_jouranl_nodes(
        child_entry_data, child_entry_query
    )
    # Function connect_to_journal() returns false if journal is alredy connected
    if not child_entry_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entry {child_entry_data.id} is already linked to parent with ID {parent_ID.parent_id}",
        )

    db.commit()
    db.refresh(child_entry_data)
    return child_entry_data


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


# FIXME Add all the logic to chech user and journal in service file
