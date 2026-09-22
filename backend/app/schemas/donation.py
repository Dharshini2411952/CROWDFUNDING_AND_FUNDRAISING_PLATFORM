from pydantic import BaseModel


class DonationCreate(BaseModel):
    campaign_id: int
    amount: float


class DonationResponse(BaseModel):
    donation_id: int
    donor_id: int
    campaign_id: int
    amount: float
    payment_status: str

    class Config:
        from_attributes = True