import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv


from pathlib import Path
load_dotenv()
backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
if backend_env.exists():
    load_dotenv(backend_env)

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

    for key in list(query_params.keys()):
        if key.lower() in (
            "ssl-mode", "ssl_mode", "ssl", "sslmode",
            "ssl_ca", "ssl-ca", "ssl_cert", "ssl-cert",
            "ssl_key", "ssl-key"
        ):
            vals = query_params.pop(key)
            if vals:
                v = str(vals[0]).upper()
                if v in ("REQUIRED", "TRUE", "1", "VERIFY_CA", "VERIFY_IDENTITY", "PREFERRED"):
                    needs_ssl = True

    new_query = urlencode(query_params, doseq=True)
    parsed = parsed._replace(query=new_query)
    url = urlunparse(parsed)

    if needs_ssl or "aivencloud.com" in url:
        connect_args["ssl"] = {"check_hostname": False}

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
