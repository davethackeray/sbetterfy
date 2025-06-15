from sqlalchemy import create_engine, Column, String, Text, Index
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
    
    id = Column(String, primary_key=True, index=True)
    spotify_client_id = Column(Text)
    spotify_client_secret = Column(Text)
    spotify_access_token = Column(Text)
    spotify_refresh_token = Column(Text)
    gemini_api_key = Column(Text)
    encryption_key = Column(Text)
    
    __table_args__ = (
        Index('idx_user_id', 'id'),
    )

def get_engine():
    """Return the SQLAlchemy engine"""
    return engine

def get_session():
    """Create a new session for database operations"""
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Initialize the database and create tables and indexes if they don't exist"""
    Base.metadata.create_all(engine)
    # Indexes are defined in the model and created automatically by SQLAlchemy
    # Additional performance optimizations can be added here if needed for future schema changes
    # Future considerations: Add compound indexes for frequently queried fields,
    # implement query caching for read-heavy operations, or consider database migration
    # to a more scalable solution like PostgreSQL if user base grows significantly.

if __name__ == "__main__":
    init_db()
