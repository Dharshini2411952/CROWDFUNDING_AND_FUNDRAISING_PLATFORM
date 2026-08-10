from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine, Base
from app import model

app = FastAPI(title="Fund AI")

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Fund AI Backend is Running"
    }


@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "Database Connected Successfully!"
        }

    except Exception as e:
        return {
            "error": str(e)
        }