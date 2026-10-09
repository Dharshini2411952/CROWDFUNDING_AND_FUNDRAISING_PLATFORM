import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv


load_dotenv()

RAW_DATABASE_URL = os.getenv("DATABASE_URL")

if not RAW_DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be configured in the backend environment")

url = RAW_DATABASE_URL
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
elif url.startswith("mysql://"):
    url = url.replace("mysql://", "mysql+pymysql://", 1)

connect_args = {}
if "mysql+pymysql://" in url:
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    needs_ssl = False
    ssl_mode_val = "REQUIRED"

    for key in list(query_params.keys()):
        if key in ("ssl-mode", "ssl_mode", "ssl"):
            vals = query_params.pop(key)
            if vals:
                v = vals[0].upper()
                if v in ("REQUIRED", "TRUE", "1", "VERIFY_CA", "VERIFY_IDENTITY", "PREFERRED"):
                    needs_ssl = True
                    if v in ("VERIFY_CA", "VERIFY_IDENTITY"):
                        ssl_mode_val = v

    new_query = urlencode(query_params, doseq=True)
    parsed = parsed._replace(query=new_query)
    url = urlunparse(parsed)

    if needs_ssl:
        connect_args["ssl"] = {"ssl_mode": ssl_mode_val}

DATABASE_URL = url

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,  # Prevent stale connection errors on Aiven/Render
    pool_recycle=300
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
