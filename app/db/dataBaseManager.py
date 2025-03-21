from app.db.connection import get_session
from app.db.models import Facture,Client,Sale,User,RequestOCR,Error
from sqlalchemy import func
class DBManager:
    def __init__(self):
        self.session = get_session()

    def CreateUser(self,email,userName,userPassword):
        user = User(userName=userName,userPassword=userPassword,userEmail = email)
        return user

    def CreateFacture(self,dict,origin,fileName):
        factureRetour = Facture(
                name=dict["billName"],  # Example name
            entrytime=func.now(),  # current session time
            facdate=dict["date"],  # current session time
        address=dict["address"],  
        pricetotal=dict["pricetotal"],  
        origin=origin,
        originDoc=fileName
        )
        return factureRetour
    
    def CreateClient(self,dict,qrCode):
            clientName = dict["destinator"]
            client = Client(name=clientName, email = dict["email"],
            gender = qrCode["custGender"],
            birth = qrCode["custBirth"])

    def CreateRequest(self,requestDict):
        pass#TODO

    def CreateEntriesFacture(self,dict,qrCode,origin,fileName,user):
        client = self.FindClient(dict,qrCode)
        if(client==None):
            #Create client
            clientName = dict["destinator"]
            client = Client(name=clientName, email = dict["email"],
            gender = qrCode["custGender"],
            birth = qrCode["custBirth"])
        user = self.GetUserByEmail(user)
        if(not user):
            return None,"ErUser non présent"
        #self.session.add(client)

        factureRetour = Facture(
                name=dict["billName"],  # Example name
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
    
    def AddRequest(request):
        pass#TODO
    
    #Partie recuperation d'élement
    def FindClient(self,dict,qrInfo):
        clientName = dict["destinator"]
        client = self.GetClientByName(clientName)
        return client

    #Partie verification qui nécessite la base de données
    def VerifyClient(self,clientName,clientEmail,clientGender,clientBirth):
        clientFound = self.GetClientByName(clientName)


    #Partie Getter
    def GetClientByName(self,clientName):
        return self.session.query(Client).filter_by(name = clientName).first()
    
    def GetUserByName(self,userName):
        return self.session.query(User).filter_by(userName=userName).first()
    
    def GetUserByEmail(self,email):
        return self.session.query(User).filter(userEmail = email).first()
    