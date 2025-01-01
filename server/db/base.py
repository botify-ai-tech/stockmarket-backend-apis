import os
import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


database_url = os.getenv("DATABASE_URL")

engine = create_engine(
    database_url,
    pool_size=100,
    max_overflow=64,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)

# Base = sqlalchemy.orm.declarative_base()


# Base.metadata.create_all(engine)
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
