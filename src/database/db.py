from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import config

SQLALCHEMY_DATABASE_URL = config.DB_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
