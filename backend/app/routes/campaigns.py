from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import Campaign
from app.schemas import CampaignCreate, CampaignResponse


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)


# Create Campaign
@router.post("/", response_model=CampaignResponse)
def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db)
):
    new_campaign = Campaign(
        creator_id=campaign_data.creator_id,
        title=campaign_data.title,
        description=campaign_data.description,
        goal_amount=campaign_data.goal_amount,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    return new_campaign


# Get All Campaigns
@router.get("/", response_model=list[CampaignResponse])
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    return campaigns


# Get One Campaign
@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.campaign_id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    return campaign