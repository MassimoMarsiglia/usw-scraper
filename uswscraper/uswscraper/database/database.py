"""
SQLAlchemy database utilities for the USW scraper
"""
import time
from sqlalchemy import Table, create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define base class for SQLAlchemy models
Base = declarative_base()

# Define example model - you can expand this with your actual models
class ScrapedItem(Base):
    __tablename__ = 'scraped_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    ip = Column(String)
    proxy = Column(String)
    data = Column(JSONB)  # Store any additional data as JSON
    
    def __repr__(self):
        return f"<ScrapedItem(id={self.id}, url='{self.url}', ip='{self.ip}')>"

class DatabaseManager:
    """SQLAlchemy database manager for USW scrapers"""
    
    def __init__(self, db_url=None):
        """Initialize with database connection string"""
        try:
            load_dotenv()
            db_url = db_url or os.getenv('DATABASE_URL', 'sqlite:///cs2_items.db')
            
        except ImportError:
            logger.warning("loadenv module not found, using environment variables directly")

        self.db_url = db_url
        self.engine = None
        self.session_factory = None
        self.Session = None
    
    def connect(self):
        """Connect to database and create session factory"""
        try:
            # self.engine = create_engine(
            #     self.db_url,
            #     # echo=False,  # Set to True to see SQL queries
            #     # pool_pre_ping=True,  # Verify connections before use
            #     # pool_recycle=3600    # Recycle connections after 1 hour
            # )
            self.engine = create_engine("postgresql+psycopg2://citizix_user:S3cret@localhost:5433/citizix_db")
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            
            logger.info(f"Connected to database: {self.db_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def init_db(self):
        """Initialize database schema"""
        try:
            if not self.engine:
                self.connect()

            Base.metadata.create_all(self.engine)

            logger.info("Database schema created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            return False
    
    def get_session(self):
        """Get a new session"""
        if not self.Session:
            self.connect()
        return self.Session()
    
    def save_item(self, item):
        """Save an item to the database"""
        session = self.get_session()
        try:
            session.add(item)
            session.commit()
            logger.debug(f"Saved item to database: {item}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving item to database: {e}")
            return False
        finally:
            session.close()
    
    def close(self):
        """Close all connections"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")


# Singleton instance
_db_manager = None

def get_db_manager():
    """Get the database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager