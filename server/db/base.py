import os
import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


database_url  = os.getenv("DATABASE_URL")

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

# Base = sqlalchemy.orm.declarative_base()

# Base.metadata.create_all(engine)