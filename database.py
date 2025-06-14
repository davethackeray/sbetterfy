from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the database URL
DATABASE_URL = "sqlite:///sbetterfy.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a base class for declarative models
Base = declarative_base()

# Define the users table as a model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    spotify_client_id = Column(Text)
    spotify_client_secret = Column(Text)
    spotify_access_token = Column(Text)
    spotify_refresh_token = Column(Text)
    gemini_api_key = Column(Text)
    encryption_key = Column(Text)

def get_engine():
    """Return the SQLAlchemy engine"""
    return engine

def get_session():
    """Create a new session for database operations"""
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Initialize the database and create tables if they don't exist"""
    Base.metadata.create_all(engine)
    # Create index on id for faster lookups (SQLAlchemy automatically handles indexes if defined in model)
    # For now, we rely on SQLAlchemy's handling; manual index creation can be added if needed

if __name__ == "__main__":
    init_db()
