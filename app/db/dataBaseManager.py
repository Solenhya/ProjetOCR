from app.db.connection import get_session
from app.db.models import Facture,Client,Sale
from sqlalchemy import func
class DBManager:
    def __init__(self):
        self.session = get_session()

    def CreateEntries(self,dict,qrCode,fileName):
        clientName = dict["destinator"]
        client = self.GetClientByName(clientName)

        if(client==None):
            #Create client
            client = Client(name=clientName, email = dict["email"],
            gender = qrCode["custGender"],
            birth = qrCode["custBirth"])

        self.session.add(client)

        factureRetour = Facture(
                name=dict["billName"],  # Example name
            entrytime=func.now(),  # current session time
            facdate=dict["date"],  # current session time
        destinator=dict["destinator"],  # Example client name, this must exist in the Client table
        address=dict["address"],  
        pricetotal=dict["pricetotal"],  
        originDoc=fileName 
        )
        for sale in dict["productSales"]:
            vente = Sale(name = sale["productName"],
            quantity = sale["productQuant"],
            price = sale["productPrice"])
            factureRetour.sales.append(vente)
        self.session.add(factureRetour)
        self.session.commit()
        return factureRetour,client


    def VerifyClient(self,clientName,clientEmail,clientGender,clientBirth):
        clientFound = self.GetClientByName(clientName)

    def GetClientByName(self,clientName):
        return self.session.query(Client).filter_by(name = clientName).first()