from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import Donation, Campaign, User
from app.schemas import DonationCreate, DonationResponse

router = APIRouter(
    prefix="/donations",
    tags=["Donations"]
)


@router.post("/", response_model=DonationResponse)
def create_donation(
    donation: DonationCreate,
    db: Session = Depends(get_db)
):
    # Check user
    user = db.query(User).filter(
        User.user_id == donation.donor_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Donor not found"
        )

    # Check campaign
    campaign = db.query(Campaign).filter(
        Campaign.campaign_id == donation.campaign_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    # Create donation
    new_donation = Donation(
        campaign_id=donation.campaign_id,
        donor_id=donation.donor_id,
        amount=donation.amount,
        message=donation.message,
        payment_method=donation.payment_method,
        transaction_id=donation.transaction_id,
        status="SUCCESS"
    )

    db.add(new_donation)

    # Update campaign amount
    campaign.current_amount = (
        campaign.current_amount + donation.amount
    )

    db.commit()
    db.refresh(new_donation)

    return new_donation


@router.get("/", response_model=list[DonationResponse])
def get_donations(
    db: Session = Depends(get_db)
):
    donations = db.query(Donation).all()
    return donations


@router.get("/{donation_id}", response_model=DonationResponse)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(
        Donation.donation_id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail="Donation not found"
        )

    return donation