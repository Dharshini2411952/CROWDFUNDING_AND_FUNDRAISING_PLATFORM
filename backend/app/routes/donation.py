import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.donation import Donation
from app.models.campaign import Campaign
from app.models.transaction import Transaction
from app.models.notification import Notification

from app.schemas.donation import (
    DonationCreate,
    DonationResponse
)
from app.routes.payments import check_and_update_campaign_expiration


router = APIRouter(
    prefix="/donations",
    tags=["Donations"]
)


# =========================================
# CREATE DONATION
# =========================================

@router.post(
    "/",
    response_model=DonationResponse
)
def create_donation(
    donation_data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only DONOR can donate
    if current_user.role != "DONOR":
        raise HTTPException(
            status_code=403,
            detail="Only donors can make donations"
        )

    if donation_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Donation amount must be greater than 0"
        )

    # Row-level lock on campaign
    campaign = (
        db.query(Campaign)
        .filter(Campaign.campaign_id == donation_data.campaign_id)
        .with_for_update()
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    if check_and_update_campaign_expiration(campaign, db):
        raise HTTPException(
            status_code=400,
            detail="Campaign has expired and cannot receive donations"
        )

    if campaign.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot donate to campaign with status '{campaign.status}'"
        )

    payment_reference = f"PAY-DIR-{uuid.uuid4().hex[:12].upper()}"

    try:
        new_donation = Donation(
            donor_id=current_user.user_id,
            campaign_id=donation_data.campaign_id,
            amount=donation_data.amount,
            status="SUCCESS"
        )

        db.add(new_donation)
        db.flush()

        transaction = Transaction(
            donation_id=new_donation.donation_id,
            payment_reference=payment_reference,
            amount=donation_data.amount,
            status="SUCCESS",
            gateway="direct",
        )
        db.add(transaction)
        db.flush()

        new_donation.transaction_id = str(transaction.transaction_id)

        old_collected = float(campaign.collected_amount or 0)
        new_collected = old_collected + donation_data.amount
        campaign.collected_amount = new_collected

        goal_amount = float(campaign.goal_amount or 0)
        goal_reached = False
        if new_collected >= goal_amount and campaign.status == "ACTIVE":
            campaign.status = "COMPLETED"
            goal_reached = True

        # Notifications
        donor_notif = Notification(
            user_id=current_user.user_id,
            title="Donation Successful",
            message=f"Thank you! Your donation of ₹{donation_data.amount:,.2f} for '{campaign.title}' was successful.",
            notification_type="DONATION_SUCCESS",
            is_read=False,
        )
        db.add(donor_notif)

        if campaign.creator_id:
            campaigner_notif = Notification(
                user_id=campaign.creator_id,
                title="New Donation Received",
                message=f"Great news! Your campaign '{campaign.title}' received a donation of ₹{donation_data.amount:,.2f}.",
                notification_type="NEW_DONATION",
                is_read=False,
            )
            db.add(campaigner_notif)

        if goal_reached:
            if campaign.creator_id:
                goal_camp_notif = Notification(
                    user_id=campaign.creator_id,
                    title="Campaign Goal Reached!",
                    message=f"Congratulations! Your campaign '{campaign.title}' has reached its goal of ₹{goal_amount:,.2f} with total raised ₹{new_collected:,.2f} and is now COMPLETED!",
                    notification_type="GOAL_REACHED",
                    is_read=False,
                )
                db.add(goal_camp_notif)

            goal_donor_notif = Notification(
                user_id=current_user.user_id,
                title="Campaign Goal Achieved!",
                message=f"Awesome! Your donation of ₹{donation_data.amount:,.2f} helped '{campaign.title}' reach 100% of its goal!",
                notification_type="GOAL_REACHED",
                is_read=False,
            )
            db.add(goal_donor_notif)

        db.commit()
        db.refresh(new_donation)

        return new_donation
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Donation failed due to error: {str(e)}"
        )



# =========================================
# GET ALL DONATIONS
# =========================================

@router.get(
    "/",
    response_model=list[DonationResponse]
)
def get_all_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only admin can see all donations
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin can view all donations"
        )

    return db.query(Donation).all()


# =========================================
# GET MY DONATIONS
# =========================================

@router.get(
    "/my",
    response_model=list[DonationResponse]
)
def get_my_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only donor can view donation history
    if current_user.role != "DONOR":
        raise HTTPException(
            status_code=403,
            detail="Only donors can view donation history"
        )

    donations = (
        db.query(Donation)
        .filter(
            Donation.donor_id ==
            current_user.user_id
        )
        .all()
    )

    return donations


# =========================================
# GET RECEIVED DONATIONS (CAMPAIGNER)
# =========================================

@router.get(
    "/received",
    response_model=list[DonationResponse]
)
def get_received_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in ["CAMPAIGNER", "ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="Only campaigners can view received donations"
        )

    # Join Donation with Campaign to get donations for campaigns created by current_user
    donations = (
        db.query(Donation)
        .join(Campaign, Donation.campaign_id == Campaign.campaign_id)
        .filter(Campaign.creator_id == current_user.user_id)
        .all()
    )

    return donations
