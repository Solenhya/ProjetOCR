# db/connection.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from sqlalchemy import URL
# Load environment variables
load_dotenv(dotenv_path="../.env")

# Build connection string
db_user = os.getenv("DBUSER")
db_password = os.getenv("DBPASSWORD")
db_host = os.getenv("DBHOST")
db_name = os.getenv("DBNAME")
db_port = os.getenv("DBPORT",5432)

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print(DATABASE_URL)
# Create engine
engine = create_engine(DATABASE_URL)

# Create thread-safe session factory
Session = scoped_session(sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
))

def get_session():
    """Get a new session from the registry."""
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