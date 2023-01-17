from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import envar

new_url = envar.database_url
new_url = new_url[8::]
new_url = "postgresql" + new_url

# SQLALCHEMY_DATABASE_URL = f'postgresql://{envar.db_username}:{envar.db_password}@{envar.db_hostname}:{envar.db_port}/{envar.db_name}'
SQLALCHEMY_DATABASE_URL = new_url


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, bind=engine, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
