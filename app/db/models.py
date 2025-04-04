from sqlalchemy.orm import declarative_base , relationship
from sqlalchemy import MetaData , String , Column , Integer ,DateTime,Date , ForeignKey ,func , Float
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
    client = relationship("Client",back_populates="factures_client",uselist=False)
    facture_request = relationship("RequestOCR",back_populates="facture",uselist=False)

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
    timePreImage = Column(Float)
    statusOCR = Column(String)
    timeOCR= Column(Float)
    statusFormatage = Column(String)
    timeFormatage = Column(Float)
    statusDB = Column(String)
    timeDB = Column(Float)
    timeEnd = Column(Float)
    user = Column(Integer,ForeignKey("users.id"))
    saved_error = relationship("Error",back_populates="from_request")
    facture = relationship("Facture",back_populates="facture_request",uselist=False)
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

    def ToDict(self):
        retour = {"id": self.id, "userEmail": self.userEmail, "userName": self.userName,"permissions":self.userRight}
        return retour

class Error(Base):
    """Table pour enregistrer lorsqu'il y a eu une erreur détécter dans le process et l'emplacement de l'image a retraiter"""
    __tablename__="erreurs"
    id = Column(Integer,primary_key=True,autoincrement=True)
    request_id = Column(Integer,ForeignKey("OCRrequests.id"),nullable=True)
    gravity = Column(String) #Est ce que l'erreur 
    result = Column(String)
    origin = Column(String)
    savedAs = Column(String)
    from_request=relationship("RequestOCR",back_populates="saved_error")