from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
import os

schema = os.getenv("DB_SCHEMA")
meta = MetaData(schema=schema)
Base = declarative_base(metadata=meta)