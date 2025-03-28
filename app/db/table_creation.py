from . import connection
from .base import Base
from sqlalchemy import inspect
from .models import User,Client,RequestOCR,Facture,Sale,Error

def CreateTable():
    engine = connection.get_engine()
    #Step 1: Create User and Client tables (no dependencies)
    User.metadata.create_all(engine)
    Client.metadata.create_all(engine)

    # Step 2: Create RequestOCR table (depends on User)
    RequestOCR.metadata.create_all(engine)

    # Step 3: Create Facture table (depends on User, Client, and RequestOCR)
    Facture.metadata.create_all(engine)

    # Step 4: Create Sale table (depends on Facture)
    Sale.metadata.create_all(engine)

    # Step 5: Create Error table (depends on RequestOCR)
    Error.metadata.create_all(engine)

def DeleteTable():
    engine = connection.get_engine()
    Base.metadata.drop_all(engine)
    print("Table Supprimer")

def DeleteRequestTable():
    engine = connection.get_engine()
    RequestOCR.metadata.drop_all(engine, tables=[RequestOCR.__table__])

def Check():
    engine = connection.get_engine()
    # Use the inspect module to check if the table exists
    inspector = inspect(engine)
    tables = inspector.get_table_names(schema="fabien")
    print(tables)