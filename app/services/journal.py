from fastapi import status, HTTPException, Depends
from sqlalchemy.orm import Session

from ..schemas import AddLinks
from .. import models

# def check_acess_parent_entry()


class JournalService:
    def __init__(
        self, current_user_ID: int, db: Session, parent_ID, child_ID: int = None
    ):
        self.parent_ID = parent_ID
        self.child_ID = child_ID
        self.current_user_ID = current_user_ID
        self.db = db

    def connect_jouranl_nodes(
        self, current_entry_data: models.Journal, current_entry_q
    ):
        if current_entry_data.link_ids:
            if self.parent_ID in current_entry_data.link_ids:
                return False
            current_entry_data.link_ids.append(self.parent_ID)
            current_entry_q.update({"link_ids": current_entry_data.link_ids})

            return current_entry_q

        else:
            list_ID = [self.parent_ID]
            current_entry_data.link_ids = list_ID
            current_entry_q.update({"link_ids": current_entry_data.link_ids})
            return current_entry_q

    def check_acess_parent_entry(self):
        journal_query = self.db.query(models.Journal).filter(
            models.Journal.id == self.parent_ID,
            models.Journal.customer_id == self.current_user_ID,
        )

        journal_data = journal_query.first()
        if journal_data is None:
            return False

        return True


def add_parent_links(
    parent_ID: AddLinks, child_ID: int, customer_data: models.Customer, db: Session
):
    current_entry_q = db.query(models.Journal).filter(models.Journal.id == child_ID)
    current_entry_data = current_entry_q.first()

    # Check if entry exists
    if current_entry_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry does not exist"
        )

    # Check if user has permission to update entry
    if current_entry_data.customer_id != customer_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this entry",
        )

    journal_validation = JournalService(
        current_user_ID=customer_data.user_id,
        db=db,
        parent_ID=parent_ID.parent_id,
        child_ID=child_ID,
    )

    if not journal_validation.check_acess_parent_entry():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"either entry with ID: `{parent_ID.parent_id}` does not exist or you do not have persmission to access it",
        )

    current_entry_q = journal_validation.connect_jouranl_nodes(
        current_entry_data, current_entry_q
    )

    if not current_entry_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entry {current_entry_data.id} is already linked to parent with ID {parent_ID.parent_id}",
        )
    else:
        db.commit()
        db.refresh(current_entry_data)
        return current_entry_data
