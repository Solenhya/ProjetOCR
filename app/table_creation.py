from dotenv import load_dotenv
load_dotenv()
from db.connection import engine  # Import the engine from connection.py
from db.models import Base  # Import Base from models.py, which contains your models

import os

print(f"Env : {os.getenv("DBUSER")}")
# Create all tables in the database
Base.metadata.create_all(engine)

print("Tables created successfully!")