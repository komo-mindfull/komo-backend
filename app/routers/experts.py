from fastapi import HTTPException, status, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..oAuth2 import get_current_user
from ..schemas import ExpertProfile, ExpertCreated, UpdateExpertProfile

router = APIRouter(tags=["Expert"])
# Route to create an expert profile
@router.post(
    "/users/expert", status_code=status.HTTP_201_CREATED, response_model=ExpertCreated
)
def create_expert(
    expert_profile: ExpertProfile,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    expert_q = db.query(models.Expert).filter(models.Expert.user_id == current_user)
    if expert_q.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expert profile already exists",
        )

    expertData = expert_profile.dict()
    print(expertData)
    expertData["user_id"] = current_user
    data = models.Expert(**expertData)
    db.add(data)
    db.commit()
    db.refresh(data)

    return data


# Route to get all expert profiles
@router.get(
    "/users/expert", status_code=status.HTTP_200_OK, response_model=list[ExpertCreated]
)
def get_all_experts(db: Session = Depends(get_db)):
    experts = db.query(models.Expert).all()
    return experts


# Route to update an expert profile
@router.put(
    "/users/expert/update", status_code=status.HTTP_200_OK, response_model=ExpertCreated
)
def update_expert(
    update_expert: UpdateExpertProfile,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):

    expert_q = db.query(models.Expert).filter(models.Expert.user_id == current_user)

    expert_data = expert_q.first()
    if not expert_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Expert profile not found"
        )

    new_expert_data = update_expert.dict()
    keyarr = []

    for i in new_expert_data:
        if new_expert_data[i] is None:
            keyarr.append(i)
    for i in keyarr:
        new_expert_data.pop(i)
    del keyarr

    new_expert_data.update({"user_id": current_user})
    expert_q.update(new_expert_data, synchronize_session=False)
    db.commit()
    db.refresh(expert_data)

    return expert_data
