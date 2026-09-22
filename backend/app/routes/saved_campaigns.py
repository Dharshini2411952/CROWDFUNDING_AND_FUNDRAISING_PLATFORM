from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.campaign import Campaign
from app.models.saved_campaign import SavedCampaign
from app.models.user import User

router = APIRouter(prefix="/saved-campaigns", tags=["Saved Campaigns"])


@router.post("/{campaign_id}", status_code=status.HTTP_201_CREATED)
def save_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    existing = (
        db.query(SavedCampaign)
        .filter(SavedCampaign.user_id == current_user.user_id, SavedCampaign.campaign_id == campaign_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Campaign already saved")

    saved = SavedCampaign(user_id=current_user.user_id, campaign_id=campaign_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)

    return {
        "success": True,
        "message": "Campaign saved successfully",
        "saved_at": saved.created_at.isoformat() if saved.created_at else None,
    }


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved = (
        db.query(SavedCampaign)
        .filter(SavedCampaign.user_id == current_user.user_id, SavedCampaign.campaign_id == campaign_id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Saved campaign not found")

    db.delete(saved)
    db.commit()
    return None


@router.get("/", response_model=dict)
def get_saved_campaigns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = (
        db.query(SavedCampaign, Campaign)
        .join(Campaign, Campaign.campaign_id == SavedCampaign.campaign_id)
        .filter(SavedCampaign.user_id == current_user.user_id)
        .order_by(SavedCampaign.created_at.desc())
        .all()
    )

    data = []
    for saved, campaign in items:
        data.append(
            {
                "saved_at": saved.created_at.isoformat() if saved.created_at else None,
                "campaign": {
                    "campaign_id": campaign.campaign_id,
                    "title": campaign.title,
                    "description": campaign.description,
                    "goal_amount": campaign.goal_amount,
                    "collected_amount": campaign.collected_amount,
                    "category": campaign.category,
                    "status": campaign.status,
                    "creator_id": campaign.creator_id,
                    "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                    "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                    "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                },
            }
        )

    return {"success": True, "data": data}