from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter

from app.schemas import Meeting, MeetingCreated
from ..database import get_db
from ..oAuth2 import get_current_user

from .. import models


router = APIRouter(
    tags = ["expert"]
)

# Route to create a new meeting
@router.post("/meeting", status_code = status.HTTP_201_CREATED, response_model=MeetingCreated)
def create_meeting(meeting_data : Meeting, db : Session = Depends(get_db), current_user : int = Depends(get_current_user)):
    customer_q = db.query(models.Customer).filter(models.Customer.user_id == current_user)
    customer_data = customer_q.first()

    if not customer_data:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User does not exist")
    
    expert_id = meeting_data.expert_id

    expert_q = db.query(models.Expert).filter(models.Expert.user_id == expert_id)
    expert_data = expert_q.first()

    if not expert_data:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Expert does not exist")
    
    new_meeting = models.Meeting(**meeting_data.dict())
    new_meeting.customer_id = current_user

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    return new_meeting

