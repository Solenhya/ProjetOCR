import os 
from dotenv import load_dotenv
import psycopg2

class productSale:
    def __init__(self,quantity,price,name):
        self.quantity = quantity
        self.price = price
        self.name = name
    
    def getTotalCost(self):
        return self.quantity*self.price
    
class facture:
    def __init__(self,billName,date,destinator,email,address,productSales,pricetotal):
        self.billName = billName
        self.date = date
        self.destinator = destinator
        self.address = address
        self.productSales = productSales
        self.pricetotal = pricetotal
        self.email = email
    def validatePrice(self):
        suposePrice = 0
        for sale in self.productSales:
            suposePrice+=sale.getTotalCost()
        priceDiff = self.pricetotal-suposePrice
        if(priceDiff>0):
            return False
        return True
    
    def validateAddress(self):
        #TODO
        return True

tableFacture="""
CREATE TABLE IF NOT EXIST fabien.factures{

}
"""


class DataBaseManager:

    def __init__(self):
        self.connection = self.se_connecter_a_la_base_de_donnees()

    def CreateTable(self):
        #TODO
        pass

    def se_connecter_a_la_base_de_donnees(self):
        load_dotenv()
        """Connexion à la base de données PostgreSQL."""
        host = os.getenv("HOST")
        utilisateur = os.getenv("USER")
        mot_de_passe = os.getenv("PASSWORD")
        nom_base_de_donnees = "postgres"
        try:
            connexion = psycopg2.connect(
                dbname=nom_base_de_donnees,
                user=utilisateur,
                password=mot_de_passe,
                host=host
            )
            print("Connexion réussie à la base de données")
            return connexion
        except psycopg2.Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
            return None
        
    def Disconnect(self):
        self.connection.close()