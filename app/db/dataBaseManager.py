from .connection import get_session
from .models import Facture,Client,Sale,User,RequestOCR,Error
from sqlalchemy import func ,select
from sqlalchemy.exc import NoResultFound
from datetime import date

class DBManager:
    def __init__(self):
        self.session = get_session()

    def CreateUser(self,email,userName,userPassword):
        user = User(userName=userName,userPassword=userPassword,userEmail = email)
        return user

    def CreateFacture(self,dict,qrCode,origin,fileName):
        factureRetour = Facture(
                name=qrCode["facName"],  # Example name
            entrytime=func.now(),  # current session time
            facdate=dict["date"],  # current session time
        address=dict["address"],  
        pricetotal=dict["pricetotal"],  
        origin=origin,
        originDoc=fileName
        )
        for sale in dict["productSales"]:
            vente = Sale(name = sale["productName"],
            quantity = sale["productQuant"],
            price = sale["productPrice"])
            factureRetour.facture_sales.append(vente)
        return factureRetour
    
    def CreateClient(self,session,dict,qrCode):
        client = FindClient(session,dict,qrCode)
        if client:
            return client
        clientName = dict["destinator"]
        client = Client(name=clientName, email = dict["email"],
        gender = qrCode["custGender"],
        birth = qrCode["custBirth"])
        return client
    
    def CreateClientSafe(self,dict,qrCode):
        client = self.FindClient(dict,qrCode)
        if client:
            erreur = self.VerifyClient(dict["destinator"],dict["email"],qrCode["custGender"],qrCode["custBirth"])
            if(erreur=="Succes"):
                return client
        clientName = dict["destinator"]
        client = Client(name=clientName, email = dict["email"],
        gender = qrCode["custGender"],
        birth = qrCode["custBirth"])
        return client

    def CreateRequest(self,requestDict):
        request = RequestOCR(
        statusPreImage = requestDict["image"]["status"],
        timePreImage = requestDict["image"]["time"],
        statusOCR = requestDict["ocr"]["status"],
        timeOCR= requestDict["ocr"]["time"],
        statusFormatage = requestDict["formatage"]["status"],
        timeFormatage = requestDict["formatage"]["time"],
        statusDB = requestDict["db"]["status"],
        timeDB = requestDict["db"]["time"],
        timeEnd = requestDict["tempsTotal"])
        today = date.today()
        request.date = today
        return request
    

    def GetRequestDict(self):
        return {"image":{"status":"NotSet","time":0},"ocr":{"status":"NotSet","time":0},"formatage":{"status":"NotSet","time":0},"db":{"status":"NotSet","time":0},"tempsTotal":0}

    def CreateError(self,gravity,result,origin,savedAs):
        erreur = Error(gravity=gravity,result=result,origin=origin,savedAs=savedAs)
        return erreur

    def CreateEntriesFacture(self,dict,qrCode,origin,fileName):
        client = self.FindClient(dict,qrCode)
        if(client==None):
            #Create client
            clientName = dict["destinator"]
            client = Client(name=clientName, email = dict["email"],
            gender = qrCode["custGender"],
            birth = qrCode["custBirth"])
        factureRetour = Facture(
                name=qrCode["facName"], 
            entrytime=func.now(),  # current session time
            facdate=dict["date"],  # current session time
        destinator=client.clientId,  # Example client name, this must exist in the Client table
        address=dict["address"],  
        pricetotal=dict["pricetotal"],  
        origin=origin,
        originDoc=fileName
        )
        factureRetour.client = client
        for sale in dict["productSales"]:
            vente = Sale(name = sale["productName"],
            quantity = sale["productQuant"],
            price = sale["productPrice"])
            factureRetour.facture_sales.append(vente)
        self.session.add(factureRetour)
        self.session.commit()
        return factureRetour , "Success"

    def CloseConnection(self):
        self.session.close()
    def RemakeSession(self):
        self.session = get_session()


    #Partie verification qui nécessite la base de données

    def ValidateFacture(self,facture,qrInfo):
        presence = self.VerifyFacturePresence(qrInfo["facName"])
        if presence["status"]!="Success":
            return presence
        client = self.VerifyClient(facture["destinator"],facture["email"],qrInfo["custGender"],qrInfo["custBirth"])
        #Si le client est bon il s'agit que de Succes
        return client

    def VerifyClient(self,clientName,clientEmail,clientGender,clientBirth):
        session = get_session()
        clientFound = GetClientByEmail(session,clientEmail)
        if(clientFound):    
            if(clientFound.name!=clientName):
                message = {"status":"Erreur Client","detail": f"{clientEmail} name in base is {clientFound.name} but in facture{clientName}"}
                session.close()
                return message
            if(clientFound.gender!=clientGender):
                message = {"status":"Erreur Client","detail": f"{clientEmail} gender in base is {clientFound.gender} but in facture {clientGender}"}
                session.close()
                return message
            if(clientBirth!=clientBirth):
                message = {"status":"Erreur Client","detail" :f"{clientEmail} birth in base is {clientFound.birth} but in facture {clientBirth}"}
                session.close()
                return message
        session.close()
        return {"status":"Success"}

    def VerifyFacturePresence(self,factureName):
        session = get_session()
        facture = GetFactureByName(session,factureName)
        if facture:
            message = {"status":"Erreur Facture","detail": f"{factureName} is already in base"}
            session.close()
            return message
        session.close()
        return {"status":"Success"}

    #Partie recuperation d'élement
def FindClient(session,dict,qrInfo):
    clientEmail = dict["email"]
    client = GetClientByEmail(session,clientEmail)
    return client

#Partie Getter
def GetClientByName(session,clientName)->Client:
    return session.query(Client).filter_by(name = clientName).first()
    
def GetClientByEmail(session,clientemail)->Client:
    return session.query(Client).filter_by(email=clientemail).first()
    
def GetFactureByName(session,factureName)->Facture:
    return session.query(Facture).filter_by(name=factureName).first()
    
def GetUserByEmail(session,userEmail):
    return session.query(User).filter_by(userEmail=userEmail).first()

def EnterFacture(session,facture:Facture,user:User,client,erreur:Error=None):
    facture.client = client
    facture.from_user = user
    SessionCommitItem(session,facture)

def EnterError(session,request:RequestOCR,erreur:Error,user:User):
    request.saved_error=[erreur]
    request.from_user=user
    SessionCommitItem(session,request)

def AddUser(session,user):
    SessionCommitItem(session,user)

def SessionCommitItem(session,item):
    session.add(item)
    session.commit()
#Partie info facture
def GetTotalSold(session):
    query = select(func.sum(Facture.pricetotal))
    total = session.execute(query).scalar_one()
    return total
def get_unique_product_count(session):
    stmt = select(func.count(Sale.name.distinct()))
    unique_product_count = session.execute(stmt).scalar_one()
    return unique_product_count

def GetNumberFacture(session):
    query = select(func.count(Facture.name))
    number = session.execute(query).scalar_one()
    return number

def GetAverageFacturePrice(session):
    query = select(func.avg(Facture.pricetotal))
    average = session.execute(query).scalar_one()
    return average

#Partie info process

def GetRequeteAverageTime(session):
    query = select(func.avg(RequestOCR.timeEnd)).filter(RequestOCR.timeEnd !=0)
    tempsaverage = session.execute(query).scalar_one()
    return tempsaverage

def GetRequeteErreur(session):
    query = select(func.count(RequestOCR.id)).filter(RequestOCR.timeEnd ==0)
    nombreErreur = session.execute(query).scalar_one()
    return nombreErreur