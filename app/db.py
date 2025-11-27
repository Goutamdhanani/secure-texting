from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Data directory inside container (mounted from host ./data)
DATA_DIR = os.environ.get("APP_DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)

# SQLite file path (persistent)
SQLITE_FILE = os.path.join(DATA_DIR, "secure_texting.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_FILE}"

# sqlite needs this for multithreaded access with SQLAlchemy + FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
