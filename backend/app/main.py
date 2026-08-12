from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.campaigns import router as campaign_router
from app.routes.donation import router as donation_router
from app.routes.comment import router as comment_router
from app.routes.reward import router as reward_router
from app.routes.payment import router as payment_router


app = FastAPI(
    title="Fund AI API",
    description="Crowdfunding and Fundraising Platform API",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================

app.include_router(auth_router)
app.include_router(campaign_router)
app.include_router(donation_router)
app.include_router(comment_router)
app.include_router(reward_router)
app.include_router(payment_router)


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "Fund AI Backend is running",
        "status": "success"
    }