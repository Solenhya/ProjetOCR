from sqlalchemy.orm import declarative_base , relationship
from sqlalchemy import MetaData , String , Column , Integer ,DateTime,Date , ForeignKey ,func
from .base import Base


class Facture(Base):
    __tablename__="factures"
    name = Column(String,primary_key=True)
    entrytime = Column(DateTime)
    facdate = Column(DateTime)
    destinator = Column(String,ForeignKey('clients.name'))
    address = Column(String)
    pricetotal = Column(Integer)
    origin=Column(String)
    originDoc = Column(String)
    proprietor = Column(String,ForeignKey("users.id")) #Qui a importer cette facture
    fromUser = relationship("User",back_populates="factures")
    sales = relationship("Sale",back_populates="facture")
    client = relationship("Client",back_populates="factures")

class Client(Base):
    __tablename__ = "clients"
    clientId = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String)
    email = Column(String)
    gender = Column(String)
    birth = Column(Date)
    factures = relationship("Facture",back_populates="client")

class Sale(Base):
    __tablename__="sales"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)
    factureName = Column(String,ForeignKey("factures.name"))
    facture = relationship("Facture",back_populates="sales")

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

class User(Base):
    __tablename__="users"
    id = Column(Integer,primary_key=True,autoincrement=True)
    useremail = Column(String)
    userPassword=Column(String)
    userRight = Column(String)
    factures = relationship("Facture",back_populates="fromUser")