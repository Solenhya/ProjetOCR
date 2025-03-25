# db/connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from sqlalchemy import URL

def create_db_engine():
    """Creates the database engine after loading environment variables."""
    # Build the connection string
    db_user = os.getenv("DBUSER")
    db_password = os.getenv("DBPASSWORD")
    db_host = os.getenv("DBHOST")
    db_name = os.getenv("DBNAME")
    db_port = os.getenv("DBPORT", 5432)
    
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print(DATABASE_URL)  # Optional: For debugging

    # Create the engine and return it
    return create_engine(DATABASE_URL,echo=True)

# Create the engine and session factory only when needed
engine = None
Session = None

def get_engine():
    """Gets the engine, creating it if it doesn't exist yet."""
    global engine
    if engine is None:
        engine = create_db_engine()
    return engine

def get_session():
    """Get a new session from the registry."""
    global Session
    if Session is None:
        Session = scoped_session(sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False
        ))
    return Session()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()