from sqlalchemy.orm import declarative_base , relationship
from sqlalchemy import MetaData , String , Column , Integer ,DateTime,Date , ForeignKey ,func
from .base import Base


class Facture(Base):
    __tablename__="factures"
    name = Column(String,primary_key=True)
    entrytime = Column(DateTime)
    facdate = Column(DateTime)
    destinatorId = Column(Integer,ForeignKey('clients.clientId'))
    address = Column(String)
    pricetotal = Column(Integer)
    origin=Column(String)
    originDoc = Column(String)
    proprietorId = Column(Integer,ForeignKey("users.id")) #Qui a importer cette facture
    request = Column(Integer,ForeignKey("OCRrequests.id"))
    from_user = relationship("User",back_populates="imported_factures")
    facture_sales = relationship("Sale",back_populates="facture")
    client = relationship("Client",back_populates="factures_client")
    facture_request = relationship("RequestOCR",back_populates="facture")

class Client(Base):
    __tablename__ = "clients"
    clientId = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String)
    email = Column(String)
    gender = Column(String)
    birth = Column(Date)
    factures_client = relationship("Facture",back_populates="client")

class Sale(Base):
    __tablename__="sales"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)
    factureName = Column(String,ForeignKey("factures.name"))
    facture = relationship("Facture",back_populates="facture_sales")

class RequestOCR(Base):
    __tablename__="OCRrequests"
    id = Column(Integer,primary_key=True,autoincrement=True)
    date = Column(Date)
    statusPreImage = Column(String)
    timePreImage = Column(Date)
    statusOCR = Column(String)
    timeOCR= Column(Date)
    statusFormatage = Column(String)
    timeFormatage = Column(Date)
    statusDB = Column(String)
    resultDB = Column(String)
    timeEnd = Column(Date)
    user = Column(Integer,ForeignKey("users.id"))
    saved_error = relationship("Error",back_populates="from_request")
    facture = relationship("Facture",back_populates="facture_request")
    from_user = relationship("User",back_populates="requests_made")

class User(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,autoincrement=True)
    userName = Column(String)
    userEmail = Column(String)
    userPassword=Column(String)
    userRight = Column(String)
    imported_factures = relationship("Facture",back_populates="from_user")
    requests_made= relationship("RequestOCR",back_populates="from_user")

class Error(Base):
    """Table pour enregistrer lorsqu'il y a eu une erreur détécter dans le process et l'emplacement de l'image a retraiter"""
    __tablename__="erreurs"
    id = Column(Integer,primary_key=True,autoincrement=True)
    request_id = Column(Integer,ForeignKey("OCRrequests.id"))
    gravity = Column(String) #Est ce que l'erreur 
    result = Column(String)
    origin = Column(String)
    savedAs = Column(String)
    from_request=relationship("RequestOCR",back_populates="saved_error")