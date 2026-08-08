from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine

app = FastAPI()

@app.get("/")
def home():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"message": "Database Connected Successfully!"}
    except Exception as e:
        return {"error": str(e)}