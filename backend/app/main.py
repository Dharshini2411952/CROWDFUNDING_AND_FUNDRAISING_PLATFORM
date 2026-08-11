from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.campaigns import router as campaign_router
from app.routes.donation import router as donation_router
from app.routes.comment import router as comment_router
from app.routes.reward import router as reward_router
from app.routes.payment import router as payment_router


app = FastAPI()


@app.get("/")
def home():
    return {"message": "Fund AI Backend is Running"}


app.include_router(auth_router)
app.include_router(campaign_router)
app.include_router(donation_router)
app.include_router(comment_router)
app.include_router(reward_router)
app.include_router(payment_router)
@app.get("/")
def home():
    return {
        "message": "Fund AI Backend is Running"
    }