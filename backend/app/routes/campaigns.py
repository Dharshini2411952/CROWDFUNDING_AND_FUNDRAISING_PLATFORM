import math
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.campaign import Campaign

from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    CampaignPaginatedResponse
)


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)


# -------------------------------------------------
# CREATE CAMPAIGN
# -------------------------------------------------

@router.post(
    "/",
    response_model=CampaignResponse
)
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only CAMPAIGNER or ADMIN can create campaigns
    if current_user.role not in ["CAMPAIGNER", "ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="Only campaigners can create campaigns"
        )

    new_campaign = Campaign(
        title=campaign.title.strip(),
        description=campaign.description.strip(),
        goal_amount=campaign.goal_amount,
        category=campaign.category.strip(),
        collected_amount=0.0,
        status="PENDING",
        creator_id=current_user.user_id
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    return new_campaign


# -------------------------------------------------
# GET ALL CAMPAIGNS (Search, Filter, Sort, Paginate)
# -------------------------------------------------

@router.get(
    "/",
    response_model=Union[CampaignPaginatedResponse, list[CampaignResponse]]
)
def get_campaigns(
    search: Optional[str] = Query(None, description="Search in title, category, description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PENDING, REJECTED, COMPLETED)"),
    sort: Optional[str] = Query("newest", description="Sort by: newest, oldest, highest_goal, highest_progress"),
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    raw_list: bool = Query(False, description="Return raw list of campaigns for backward compatibility"),
    db: Session = Depends(get_db)
):

    query = db.query(Campaign)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Campaign.title.ilike(s),
                Campaign.category.ilike(s),
                Campaign.description.ilike(s)
            )
        )

    if category:
        query = query.filter(Campaign.category.ilike(category.strip()))

    if status:
        query = query.filter(Campaign.status.ilike(status.strip()))

    # Sorting
    if sort == "oldest":
        query = query.order_by(Campaign.created_at.asc(), Campaign.campaign_id.asc())
    elif sort == "highest_goal":
        query = query.order_by(Campaign.goal_amount.desc(), Campaign.campaign_id.desc())
    elif sort == "highest_progress":
        query = query.order_by(Campaign.collected_amount.desc(), Campaign.campaign_id.desc())
    else:  # newest default
        query = query.order_by(Campaign.created_at.desc(), Campaign.campaign_id.desc())

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    items = query.offset((page - 1) * page_size).limit(page_size).all()

    if raw_list:
        return items

    return CampaignPaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )



# -------------------------------------------------
# GET ONE CAMPAIGN
# -------------------------------------------------

@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse
)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):

    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.campaign_id == campaign_id
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    return campaign


# -------------------------------------------------
# UPDATE CAMPAIGN
# -------------------------------------------------

@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse
)
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.campaign_id == campaign_id
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    # Admin can update any campaign
    # Campaigner can update only their own campaign
    if (
        current_user.role != "ADMIN"
        and campaign.creator_id != current_user.user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can update only your own campaign"
        )

    if campaign_data.title is not None:
        campaign.title = campaign_data.title

    if campaign_data.description is not None:
        campaign.description = campaign_data.description

    if campaign_data.goal_amount is not None:
        campaign.goal_amount = campaign_data.goal_amount

    if campaign_data.category is not None:
        campaign.category = campaign_data.category

    db.commit()
    db.refresh(campaign)

    return campaign


# -------------------------------------------------
# DELETE CAMPAIGN
# -------------------------------------------------

@router.delete(
    "/{campaign_id}"
)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.campaign_id == campaign_id
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    # Admin can delete any campaign
    # Campaigner can delete only their own campaign
    if (
        current_user.role != "ADMIN"
        and campaign.creator_id != current_user.user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own campaign"
        )

    db.delete(campaign)
    db.commit()

    return {
        "message": "Campaign deleted successfully"
    }