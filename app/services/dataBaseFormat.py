import os 
from dotenv import load_dotenv
import psycopg2
import re
from tqdm import tqdm

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
    def __init__(self,billName,date,destinator,email,address,productSales,pricetotal,qrInfo:QRInfo):
        self.billName = billName
        self.date = date
        self.destinator = destinator
        self.address = address
        self.productSales = productSales
        self.pricetotal = pricetotal
        self.email = email
        self.qrInfo = qrInfo

    def fromDict(dict):
        listeSale = []
        listDict = dict["productSales"]
        for sale in listDict:
            ajout = productSale(name=sale["productName"],quantity=sale["productQuant"],price=sale["productPrice"])
            listeSale.append(ajout)
        return facture(
        billName = dict["billName"],
        date=dict["date"],
        destinator=dict["destinator"],
        email=dict["email"],
        address=dict["address"],
        productSales=listeSale,
        pricetotal=dict["pricetotal"],
        qrInfo=None
        )

    def ValidateFullness(self):
        if(self.billName==""):
            tqdm.write("Missing billName")
            return False
        if(self.date==""):
            tqdm.write("Missing date")
            return False
        if(self.destinator==""):
            tqdm.write("Missing destinator")
            return False
        if(self.address==""):
            tqdm.write("Missing address")
            return False
        if(self.pricetotal==""):
            tqdm.write("Missing price")
            return False
        if(self.email==""):
            tqdm.write("Missing email")
            return False
        if(len(self.productSales)==0):
            tqdm.write("Missing sales")
            return False
        if(self.qrInfo==None):
            tqdm.write("Missing qrInfo")
            return False
        return True

    def validatePrice(self):
        suposePrice = 0
        for sale in self.productSales:
            suposePrice+=sale.getTotalCost()
        priceDiff = self.pricetotal-suposePrice
        if(priceDiff>0):
            tqdm.write(f" Prix suposer {suposePrice} prix total {self.pricetotal} difference {priceDiff}")
            return False
        return True

    def validateQR(self):
        if self.qrInfo.facName != self.billName:
            tqdm.write("ErqrCode sur le name")
            return False
        date = self.qrInfo.facDate
        simplifiedDate = date.split()[0]
        if simplifiedDate != self.date:
            tqdm.write("ErqrCode sur la date")
            return False
        return True
    
    #Function to reformate behind OCR error
    def ReFormat(self):
        pass#TODO


class AZdbManager:
    tableFacture="""
    CREATE TABLE IF NOT EXISTS factures(
    name VARCHAR(200) PRIMARY KEY,
    entrytime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    facdate VARCHAR(200),
    destinator VARCHAR(200),
    address VARCHAR(500),
    pricetotal INT,
    originDoc VARCHAR(200)
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

    def GetFactureDoc(self,document):
        curseur = self.GetCursor()
        commande  = f"SELECT * FROM factures WHERE originDoc = '{document}'"
        curseur.execute(commande)
        retour = curseur.fetchall()
        curseur.close()
        return retour

    def GetFacture(self,facture:facture):
        curseur = self.GetCursor()
        commande  = f"SELECT * FROM factures WHERE name = '{facture.billName}'"
        curseur.execute(commande)
        retour = curseur.fetchall()
        curseur.close()
        return retour

    #Fonction de validation de la facture
    def ValidateFacture(self,facture:facture):
        if(len(self.GetFacture(facture))>0):
            return "ErDuplication"
        return "Success"
    
    #Fait la validation du client
    def ValidateClient(self,facture:facture):
        client = self.getClientU(facture.destinator)
        if(len(client)==0):
            return (True,"Success")
        client = client[0]
        clientEmail = client[1]
        clientGender = client[2]
        clientBirth = client[3]
        if(clientEmail!=facture.email):
            return(False,"Erclient erreur sur l'email")
        if(clientGender!=facture.qrInfo.custGender):
            return(False,"Erclient erreur sur le genre")
        if(clientBirth!=facture.qrInfo.custBirth):
            return(False,"Erclient erreur sur la naissance")
        return(False,"Success")

    #Pour recuperer les clients de maniere unique
    def getClientU(self,clientName):
        curseur = self.GetCursor()
        commande  = f"SELECT * FROM clients WHERE name = '{clientName}'"
        curseur.execute(commande)
        retour = curseur.fetchall()
        curseur.close()
        return retour

    def DataBaseValidation(self,facture,fileName):
        retour = {"facturePresence":{"status":"Absent","fromFile":"","conflict":"False"},"clientInfo":{
            "clientPresence":"False",
            "EmailValidation":"False",
            "GenderValidation":"False",
            "BirthValidation":"False"
        }}
        factures = self.GetFactureDoc(fileName)
        if(len(factures)>0):
            retour["facturePresence"]["status"]="True"
            retour["facturePresence"]["fromFile"]=factures[0][6]
            if(retour["facturePresence"]["fromFile"]!=fileName):
                retour["facturePresence"]["conflict"]="True"
        client = self.getClientU(facture.destinator)
        if len(client)>0:
            retour["clientInfo"]["clientPresence"]="True"
            client = client[0]
            clientEmail = client[1]
            clientGender = client[2]
            clientBirth = client[3]
            if(clientEmail==facture.email):
                retour["clientInfo"]["EmailValidation"]="True"
            if(clientGender==facture.qrInfo.custGender):
                retour["clientInfo"]["GenderValidation"]="True"
            if(clientBirth==facture.qrInfo.custBirth):
                retour["clientInfo"]["BirthValidation"]="True"
        return retour
    
    #La fonction qui gere les facture (validation puis insertion)
    def ManageFacture(self,facture:facture,fileName):
        result = self.ValidateFacture(facture)
        if(result=="Success"):
            createClient , message = self.ValidateClient(facture)
            if(message=="Success"):
                self.insertFacture(facture,createClient,fileName)
            return message
        return result

    #Fait l'insertion une fois les verifications faite
    def insertFacture(self,facture:facture,createClient,fileName):
        factureCommande = "INSERT INTO factures (name,facdate,destinator,address,pricetotal,originDoc) VALUES (%s,%s,%s,%s,%s,%s);"
        curseur=self.GetCursor()
        curseur.execute(factureCommande,
                        (facture.qrInfo.facName,facture.qrInfo.facDate,facture.destinator,facture.address,facture.pricetotal,fileName))
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
            tqdm.write("Connexion réussie à la base de données")
            return connexion
        except psycopg2.Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
            return None
        
    def Disconnect(self):
        self.connection.close()
        print("Deconnexion de la base de donnée")