from . import connection
from .base import Base

def CreateTable():
    engine = connection.get_engine()
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

def DeleteTable():
    engine = connection.get_engine()
    Base.metadata.drop_all(engine)
    print("Table Supprimer")