import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.models.transaction import Transaction
from app.models.user import User
from app.models.notification import Notification

router = APIRouter(prefix="/payments", tags=["Payments"])


def check_and_update_campaign_expiration(campaign: Campaign, db: Session) -> bool:
    """
    If campaign has an end_date in the past and is currently ACTIVE or PENDING,
    mark it as EXPIRED and notify the creator. Returns True if campaign is expired.
    """
    if campaign.end_date:
        end_dt = campaign.end_date
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if now > end_dt:
            if campaign.status in ["ACTIVE", "PENDING"]:
                campaign.status = "EXPIRED"
                if campaign.creator_id:
                    exp_notif = Notification(
                        user_id=campaign.creator_id,
                        title="Campaign Expired",
                        message=f"Your campaign '{campaign.title}' passed its end date without reaching its goal and is now EXPIRED.",
                        notification_type="CAMPAIGN_EXPIRED",
                        is_read=False
                    )
                    db.add(exp_notif)
                db.commit()
            return True
    return False


@router.post("/create")
def create_payment(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "DONOR":
        raise HTTPException(status_code=403, detail="Only donors can make payments")

    campaign_id = payload.get("campaign_id")
    try:
        amount = float(payload.get("amount", 0) or 0)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid donation amount")

    if not campaign_id or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid campaign or donation amount must be greater than 0")

    campaign = db.query(Campaign).filter(Campaign.campaign_id == int(campaign_id)).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if check_and_update_campaign_expiration(campaign, db):
        raise HTTPException(status_code=400, detail="Campaign has expired and cannot receive donations")

    if campaign.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot donate to campaign with status '{campaign.status}'"
        )

    payment_reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"
    return {
        "success": True,
        "message": "Mock payment created successfully",
        "data": {
            "payment_reference": payment_reference,
            "amount": float(amount),
            "campaign_id": int(campaign_id),
            "gateway": "mock",
            "status": "PENDING",
        },
    }


@router.post("/verify")
def verify_payment(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "DONOR":
        raise HTTPException(status_code=403, detail="Only donors can verify payments")

    payment_reference = payload.get("payment_reference")
    if not payment_reference or not str(payment_reference).strip():
        raise HTTPException(status_code=400, detail="payment_reference is required")
    payment_reference = str(payment_reference).strip()

    try:
        amount = float(payload.get("amount", 0) or 0)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid donation amount")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Donation amount must be greater than 0")

    try:
        campaign_id = int(payload.get("campaign_id", 0) or 0)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    # Safe payment-reference / idempotency check
    existing_tx = db.query(Transaction).filter(Transaction.payment_reference == payment_reference).first()
    if existing_tx:
        if existing_tx.status == "SUCCESS":
            raise HTTPException(
                status_code=409,
                detail=f"Duplicate payment request: Payment reference '{payment_reference}' has already been processed successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Payment reference '{payment_reference}' was previously processed with status '{existing_tx.status}'"
            )

    # Row-level lock on campaign for safe concurrent updates
    campaign = (
        db.query(Campaign)
        .filter(Campaign.campaign_id == campaign_id)
        .with_for_update()
        .first()
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if check_and_update_campaign_expiration(campaign, db):
        raise HTTPException(status_code=400, detail="Campaign has expired and cannot receive donations")

    if campaign.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot donate to campaign with status '{campaign.status}'"
        )

    req_status = payload.get("status", "SUCCESS")
    if req_status not in ["SUCCESS", "FAILED"]:
        req_status = "SUCCESS"

    try:
        if req_status == "FAILED":
            # Failed payment path: record failed donation & transaction, notify donor, do NOT touch campaign total
            failed_donation = Donation(
                donor_id=current_user.user_id,
                campaign_id=campaign_id,
                amount=amount,
                status="FAILED",
            )
            db.add(failed_donation)
            db.flush()

            failed_tx = Transaction(
                donation_id=failed_donation.donation_id,
                payment_reference=payment_reference,
                amount=amount,
                status="FAILED",
                gateway="mock",
            )
            db.add(failed_tx)

            failed_notif = Notification(
                user_id=current_user.user_id,
                title="Payment Failed",
                message=f"Your payment of ₹{amount:,.2f} for campaign '{campaign.title}' failed or was declined. No funds were charged.",
                notification_type="PAYMENT_FAILED",
                is_read=False,
            )
            db.add(failed_notif)

            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Payment verification failed or payment was declined by gateway"
            )

        # Successful payment path
        donation = Donation(
            donor_id=current_user.user_id,
            campaign_id=campaign_id,
            amount=amount,
            status="SUCCESS",
        )
        db.add(donation)
        db.flush()

        transaction = Transaction(
            donation_id=donation.donation_id,
            payment_reference=payment_reference,
            amount=amount,
            status="SUCCESS",
            gateway="mock",
        )
        db.add(transaction)
        db.flush()

        donation.transaction_id = str(transaction.transaction_id)

        # Increment campaign collected amount
        old_collected = float(campaign.collected_amount or 0)
        new_collected = old_collected + amount
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
            message=f"Thank you! Your donation of ₹{amount:,.2f} for '{campaign.title}' was successful.",
            notification_type="DONATION_SUCCESS",
            is_read=False,
        )
        db.add(donor_notif)

        if campaign.creator_id:
            campaigner_notif = Notification(
                user_id=campaign.creator_id,
                title="New Donation Received",
                message=f"Great news! Your campaign '{campaign.title}' received a donation of ₹{amount:,.2f}.",
                notification_type="NEW_DONATION",
                is_read=False,
            )
            db.add(campaigner_notif)

        if goal_reached:
            if campaign.creator_id:
                goal_camp_notif = Notification(
                    user_id=campaign.creator_id,
                    title="Campaign Goal Reached!",
                    message=f"Congratulations! Your campaign '{campaign.title}' has reached its goal of ₹{goal_amount:,.2f} with total collected ₹{new_collected:,.2f} and is now COMPLETED!",
                    notification_type="GOAL_REACHED",
                    is_read=False,
                )
                db.add(goal_camp_notif)

            goal_donor_notif = Notification(
                user_id=current_user.user_id,
                title="Campaign Goal Achieved!",
                message=f"Awesome! Your donation of ₹{amount:,.2f} helped '{campaign.title}' reach 100% of its goal!",
                notification_type="GOAL_REACHED",
                is_read=False,
            )
            db.add(goal_donor_notif)

        db.commit()
        db.refresh(donation)
        db.refresh(transaction)
        db.refresh(campaign)

        return {
            "success": True,
            "message": "Payment verified and donation recorded",
            "data": {
                "donation_id": donation.donation_id,
                "transaction_id": transaction.transaction_id,
                "campaign_id": campaign_id,
                "amount": amount,
                "status": "SUCCESS",
                "campaign_status": campaign.status,
                "collected_amount": campaign.collected_amount,
                "goal_amount": campaign.goal_amount,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Payment verification failed due to database or system error: {str(e)}"
        )


