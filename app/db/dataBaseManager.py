from app.db.connection import get_session
from app.db.models import Facture,Client,Sale,User,RequestOCR,Error
from sqlalchemy import func
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
        resultDB = requestDict["db"]["time"],
        timeEnd = requestDict["timeFinal"])
        return request
    
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

    
    #Partie recuperation d'élement
    def FindClient(self,dict,qrInfo):
        clientEmail = dict["email"]
        client = self.GetClientByEmail(clientEmail)
        return client

    #Partie verification qui nécessite la base de données
    def VerifyClient(self,clientName,clientEmail,clientGender,clientBirth):
        clientFound = self.GetClientByEmail(clientEmail)
        if(clientFound.name!=clientName):
            message = f"Erreur Client : {clientEmail} name in base is {clientFound.name} but in facture {clientName}"
            return message
        if(clientFound.gender!=clientGender):
            message = f"Erreur Client : {clientEmail} gender in base is {clientFound.gender} but in facture {clientGender}"
            return message
        if(clientBirth!=clientBirth):
            message = f"Erreur Client : {clientEmail} birth in base is {clientFound.birth} but in facture {clientBirth}"
            return message
        return "Success"

    def VerifyFacturePresence(self,factureName):
        facture = self.GetFactureByName(factureName)
        if facture:
            message = f"Erreur Facture : {factureName} is already in base"
            return message
        return "Success"
    
    #Partie Getter
    def GetClientByName(self,clientName)->Client:
        return self.session.query(Client).filter_by(name = clientName).first()
    
    def GetClientByEmail(self,clientemail):
        return self.session.query(Client).filter_by(email=clientemail).first()
    
    def GetFactureByName(self,factureName):
        return self.session.query(Facture).filter_by(name=factureName).first()
    

def EnterRequestSession(info):
    
    pass

def SuccessStichAdd(facture,client,user,request):
    facture.client = client
    facture.fromUser = user
    facture.facture_request = request
    request.from_user=user
    SessionCommitItem(facture)

def ErrorStitchAdd(erreur,request,user,facture=None,client=None):
    erreur.from_request = request
    request.from_user = user
    if facture and client:
        facture.client = client
        facture.fromUser = user
        facture.facture_request = request
    SessionCommitItem(erreur)

def AddUser(user):
    SessionCommitItem(user)

def SessionCommitItem(item):
    session = get_session()
    session.add(item)
    session.commit()
    session.close