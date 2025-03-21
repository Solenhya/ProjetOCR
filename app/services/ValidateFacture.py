
def ValidateFullnessDict(facture):
        retour = {"total":False,"billName":False,"date":False,"destinator":False,"address":False,"priceTotal":False,"email":False,"productSales":False,"qrInfo":{"présence":False,"billName":False,"billDate":False,"custGender":False,"custBirth":False}}
        if(not facture["billName"]==""):
            retour["billName"]=True
        if(not facture["date"]==""):
            retour["date"]=True
        if(not facture["destinator"]==""):
            retour["destinator"]=True
        if(not facture["address"]==""):
            retour["address"]=True
        if(not facture["pricetotal"]==""):
            retour["priceTotal"]=True
        if(not facture["email"]==""):
            retour["email"]=True
        if(not (len(facture["productSales"])==0)):
            retour["productSales"]=True
        #TODO
        if(facture["qrInfo"]==None):
            print("Missing qrInfo")
            return False
        return retour

def ValidateFullness(ocrInfo,QRInfo):
        if(ocrInfo["billName"]==""):
            print("Missing billName")
            return False
        if(ocrInfo["date"]==""):
            print("Missing date")
            return False
        if(ocrInfo["destinator"]==""):
            print("Missing destinator")
            return False
        if(ocrInfo["address"]==""):
            print("Missing address")
            return False
        if(ocrInfo["pricetotal"]==""):
            print("Missing price")
            return False
        if(ocrInfo["email"]==""):
            print("Missing email")
            return False
        if(len(ocrInfo["productSales"])==0):
            print("Missing sales")
            return False
        if(QRInfo==None):
            print("Missing qrInfo")
            return False
        return True


def ValidatePrice(facture):
    listeVente = facture["productSales"]
    calcTotal = CalculateTotal(listeVente)
    difference = calcTotal-facture["pricetotal"]
    if(difference>0):
        return False
    return True

def ValidateQR(facture,qrInfo):
    if qrInfo["facName"] != facture["billName"]:
        return False
    date = qrInfo["facDate"]
    simplifiedDate = date.split()[0]
    if simplifiedDate != facture["date"]:
        return False
    return True

def CalculateTotal(listeSale):
    total=0
    for sale in listeSale:
        total+=sale["productQuant"]*sale["productPrice"]
    return total

#Fait les validation possible a partir de la facture
def ValidateFacture(facture,qrInfo):
    if(not ValidateFullness(facture,qrInfo)):
        return "Erfacture Non complete"
    if(not ValidatePrice(facture)):
        return "Erfacture price non Egale"
    if(not ValidateQR(facture,qrInfo)):
        print("Erreur de validation qr forcer")
        #return "Erfacture info non validé qrCode"
    return "Success"
