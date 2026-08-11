from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import Reward
from app.schemas import RewardCreate, RewardResponse


router = APIRouter(
    prefix="/rewards",
    tags=["Rewards"]
)


@router.post("/", response_model=RewardResponse)
def create_reward(
    reward: RewardCreate,
    db: Session = Depends(get_db)
):
    new_reward = Reward(
        campaign_id=reward.campaign_id,
        title=reward.title,
        description=reward.description,
        min_amount=reward.min_amount,
        quantity=reward.quantity,
        available_quantity=reward.available_quantity
    )

    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)

    return new_reward


@router.get("/", response_model=list[RewardResponse])
def get_rewards(db: Session = Depends(get_db)):
    return db.query(Reward).all()


@router.get("/{reward_id}", response_model=RewardResponse)
def get_reward(
    reward_id: int,
    db: Session = Depends(get_db)
):
    reward = db.query(Reward).filter(
        Reward.reward_id == reward_id
    ).first()

    if not reward:
        raise HTTPException(
            status_code=404,
            detail="Reward not found"
        )

    return reward