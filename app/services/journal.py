from fastapi import status, HTTPException, Depends
from sqlalchemy.orm import Session

from ..schemas import AddLinks
from .. import models

# def check_acess_parent_entry()


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

    journal_query = db.query(models.Journal).filter(
        models.Journal.id == parent_ID.parent_id,
        models.Journal.customer_id == customer_data.user_id,
    )
    journal_data = journal_query.first()
    if journal_data is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized to link parent_ID {} to this entry".format(
                parent_ID.parent_id
            ),
        )
    # Check if link to parent entry exists

    if current_entry_data.link_ids:
        if parent_ID.parent_id in current_entry_data.link_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This entry is already linked to this parent",
            )
        current_entry_data.link_ids.append(parent_ID.parent_id)
        current_entry_q.update({"link_ids": current_entry_data.link_ids})

        db.commit()
        db.refresh(current_entry_data)
        return current_entry_data

    else:
        list_ID = [parent_ID.parent_id]
        current_entry_data.link_ids = list_ID
        db.commit()
        db.refresh(current_entry_data)
        return current_entry_data
