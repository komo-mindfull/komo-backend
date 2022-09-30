from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import envar

# SQLALCHEMY_DATABASE_URL = f'postgresql://{envar.db_username}:{envar.db_password}@{envar.db_hostname}:{envar.db_port}/{envar.db_name}'
SQLALCHEMY_DATABASE_URL = envar.database_url


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, bind=engine, autoflush=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""while True:
    try:
        conn = connect(host='localhost', database='fastapi',
                       user='postgres', password='password', port='5001', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull")
        break
    except Exception as error:
        print("Connection failed: ", error)"""
