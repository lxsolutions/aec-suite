from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable or use default SQLite path
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///land_listings.db')

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # Import all modules here that might define models
    from models.land_listing import LandListing
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return db_session