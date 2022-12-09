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
            current_entry_q.update(
                {"link_ids": current_entry_data.link_ids}, synchronize_session=False
            )

            return current_entry_q

        else:
            list_ID = [self.parent_ID]
            current_entry_data.link_ids = list_ID
            current_entry_q.update(
                {"link_ids": current_entry_data.link_ids}, synchronize_session=False
            )
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
