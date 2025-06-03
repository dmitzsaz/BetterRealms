from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

SQLALCHEMY_DATABASE_URL = \
    (f"mysql+pymysql://{settings.DB_USER_NAME}:{settings.DB_ROOT_PASSWORD.replace('@', '%40')}"
     f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_pre_ping=True,
                       pool_recycle=300)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db