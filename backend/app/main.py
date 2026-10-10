import os
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.database import Base, engine
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.campaigns import router as campaign_router
from app.routes.comments import router as comments_router
from app.routes.donation import router as donation_router
from app.routes.notifications import router as notifications_router
from app.routes.payments import router as payments_router
from app.routes.saved_campaigns import router as saved_campaigns_router


app = FastAPI(
    title="Fund AI API",
    description="Crowdfunding and Fundraising Platform API",
    version="1.0.0"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    for err in errors:
        msg = err.get("msg", "")
        if msg.startswith("Value error, "):
            msg = msg[13:]
        messages.append(msg)
    detail_msg = ", ".join(messages) if messages else "Validation error"
    return JSONResponse(
        status_code=422,
        content={"detail": detail_msg}
    )


@app.on_event("startup")
def startup_db_init():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.")
    except Exception as exc:
        print(f"Startup DB Error (Check DATABASE_URL & Aiven connectivity): {exc}")


raw_cors = os.getenv("CORS_ORIGINS", "")
parsed_origins = [origin.strip().rstrip("/") for origin in raw_cors.split(",") if origin.strip()]

if not parsed_origins or "*" in parsed_origins:
    allowed_origins = ["*"]
else:
    expanded = set()
    for origin in parsed_origins:
        expanded.add(origin)
        expanded.add(origin + "/")
    # Always allow local dev ports in case of local testing
    local_defaults = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175"
    ]
    for loc in local_defaults:
        expanded.add(loc)
        expanded.add(loc + "/")
    allowed_origins = list(expanded)

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