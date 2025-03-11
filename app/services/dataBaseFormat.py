import os 
from dotenv import load_dotenv
import psycopg2
import re

class productSale:
    def __init__(self,quantity,price,name):
        self.quantity = quantity
        self.price = price
        self.name = name
    
    def getTotalCost(self):
        return self.quantity*self.price

class QRInfo:
    def __init__(self,facName,facDate,custGender,custBirth):
        self.facName = facName
        self.facDate = facDate
        self.custGender = custGender
        self.custBirth = custBirth
     

class facture:
    def __init__(self,billName,date,destinator,email,address,productSales,pricetotal,qrInfo):
        self.billName = billName
        self.date = date
        self.destinator = destinator
        self.address = address
        self.productSales = productSales
        self.pricetotal = pricetotal
        self.email = email
        self.qrInfo = qrInfo

    def validatePrice(self):
        suposePrice = 0
        for sale in self.productSales:
            suposePrice+=sale.getTotalCost()
        priceDiff = self.pricetotal-suposePrice
        if(priceDiff>0):
            return False
        return True

    def validateQR(self):
        if self.qrInfo.facName != self.billName:
            return False
        date = self.qrInfo.facDate
        simplifiedDate = date.split()[0]
        if simplifiedDate != self.date:
            return False
        return True
        


class AZdbManager:
    tableFacture="""
    CREATE TABLE IF NOT EXISTS factures(
    name VARCHAR(200) PRIMARY KEY,
    entrytime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    facdate VARCHAR(200),
    destinator VARCHAR(200),
    address VARCHAR(500),
    pricetotal INT
    );
    """
    #le prix est en centimes
    tableSales="""
    CREATE TABLE IF NOT EXISTS sales (
        id SERIAL PRIMARY KEY,
        fromfacture VARCHAR(200),
        product VARCHAR(1000),
        quantity INT,
        price INT
    );
    """

    tableClient = """
    CREATE TABLE IF NOT EXISTS clients(
        name VARCHAR(200) PRIMARY KEY,
        email VARCHAR(500),
        gender VARCHAR(5),
        birth VARCHAR(200)
    );
    """

    def __init__(self,schema):
        self.connection = self.se_connecter_a_la_base_de_donnees()
        self.schema = schema
        self.schemaSet = False

    def GetCursor(self):
        cursor = self.connection.cursor()
        cursor.execute(f"SET search_path TO {self.schema};")
        return cursor
    
    def CreateTable(self):
        curseur = self.GetCursor()
        curseur.execute(AZdbManager.tableFacture)
        curseur.execute(AZdbManager.tableSales)
        curseur.execute(AZdbManager.tableClient)
        curseur.close()

    def GetFacture(self,facture:facture):
        curseur = self.GetCursor()
        commande  = f"SELECT * FROM factures WHERE name = '{facture.billName}'"
        curseur.execute(commande)
        retour = curseur.fetchall()
        curseur.close()
        return retour

    def ValidateFacture(self,facture:facture):
        if(facture.qrInfo==None):
            return "ErQR"
        if(not facture.validatePrice):
            return "PriceEr"
        if(not facture.validateQR):
            return "ErValQR"
        if(len(self.GetFacture(facture))>0):
            return "ErDuplication"
        return "Success"
    
    #Pour recuperer les clients de maniere unique
    def getClientU(self,clientName):
        curseur = self.GetCursor()
        commande  = f"SELECT * FROM clients WHERE name = '{clientName}'"
        curseur.execute(commande)
        retour = curseur.fetchall()
        curseur.close()
        return retour

    #La fonction qui gere les facture (validation puis insertion)
    def ManageFacture(self,facture:facture):
        result = self.ValidateFacture(facture)
        if(result=="Success"):
            createClient = True
            if(len(self.getClientU(facture.destinator))>0):
                createClient=False
            self.insertFacture(facture,createClient)
        return result

    #Fait l'insertion une fois les verifications faite
    def insertFacture(self,facture:facture,createClient):
        factureCommande = "INSERT INTO factures (name,facdate,destinator,address,pricetotal) VALUES (%s,%s,%s,%s,%s);"
        curseur=self.GetCursor()
        curseur.execute(factureCommande,(facture.billName,facture.date,facture.destinator,facture.address,facture.pricetotal))
        self.connection.commit()
        for sale in facture.productSales:
            self.insertSale(sale,facture.billName,curseur)
        if(createClient):
            self.insertClient(facture.destinator,facture.email,facture.qrInfo.custBirth,facture.qrInfo.custGender,curseur)
        #self.insertClient(facture.destinator,facture.email,"Vide","X",curseur)
        
    def insertSale(self,sale:productSale,factureName,curseur):
        commande = "INSERT INTO sales (fromfacture,product,quantity,price) VALUES (%s,%s,%s,%s);"
        curseur.execute(commande,(factureName,sale.name,sale.quantity,sale.price))
        self.connection.commit()
        #Comment gerer ne pas inserer la meme commande

    def insertClient(self,clientName,clientEmail,birthDate,gender,curseur):
        commande = "INSERT INTO clients (name,email,gender,birth) VALUES (%s,%s,%s,%s);"
        curseur.execute(commande,(clientName,clientEmail,gender,birthDate))
        self.connection.commit()
        #besoin de gerer le fait qu'il puisse ne pas etre bon : exemple exister deja mais pas avec la meme address mail. 
        #Eventuellement gerer le QR Code

    def se_connecter_a_la_base_de_donnees(self):
        load_dotenv()
        """Connexion à la base de données PostgreSQL."""
        host = os.getenv("DBHOST")
        utilisateur = os.getenv("DBUSER")
        mot_de_passe = os.getenv("DBPASSWORD")
        nom_base_de_donnees = os.getenv("DBNAME")
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
        print("Deconnexion de la base de donnée")