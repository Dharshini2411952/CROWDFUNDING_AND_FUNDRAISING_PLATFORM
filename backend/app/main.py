from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.campaigns import router as campaign_router
from app.routes.comments import router as comments_router
from app.routes.donation import router as donation_router
from app.routes.notifications import router as notifications_router
from app.routes.payments import router as payments_router
from app.routes.saved_campaigns import router as saved_campaigns_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Fund AI API",
    description="Crowdfunding and Fundraising Platform API",
    version="1.0.0"
)


import os

raw_cors = os.getenv("CORS_ORIGINS", "")
allowed_origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
if not allowed_origins:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(auth_router)
app.include_router(campaign_router)
app.include_router(donation_router)
app.include_router(payments_router)
app.include_router(comments_router)
app.include_router(notifications_router)
app.include_router(saved_campaigns_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {
        "message": "Fund AI Backend is running",
        "status": "success"
    }