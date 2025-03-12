import re
from . import dataBaseFormat as dbF

def GetName(ligne):
    pattern = r"(?<=INVOICE\s)FAC\S*"
    # Trouve la premiere instance du patern
    match = re.search(pattern, ligne)
    if match:
        return(match.group(0))

def GetDate(ligne):
    #On recherche le "mot" qui suis Issue date
    pattern = r"(?<=Issue date\s)\S*"
    match = re.search(pattern,ligne)
    if match:
        return(match.group(0))
    
def GetProductLigne(ligne):
    #On determine si il s'agit d'une ligne de prix par la présence de chiffre x chiffre
    patternVerification = r"\d+\s*x\s*\d+"
    matchVeri = re.search(patternVerification,ligne)
    if matchVeri:
        patternText = r"(.*)(\d+)\s*x\s*([0-9.]+)"
        match = re.search(patternText, ligne)
        productPrice = ConvertPrice(match.group(3))
        productPrice = ConvertPrice(match.group(3))
        productQuant = int(match.group(2))
        sale = dbF.productSale(productQuant,productPrice,match.group(1))
        return sale
        #return {"productName":match.group(1),"productQuant":match.group(2),"productPrice":productPrice}

def GetEmail(ligne):
    pattern = r"\S+@\S+\.\S+"
    match = re.search(pattern,ligne)
    if match:
        return(match.group(0))

def GetDestinator(ligne):
    pattern = r"(?<=Bill to\s).+"
    match = re.search(pattern,ligne)
    if match:
        return(match.group(0))

def GetTotal(ligne):
    pattern = r"(?i)(?<=Total\s)[0-9.]+"
    match = re.search(pattern,ligne)
    if match:
        totalPrice = ConvertPrice(match.group(0))
        return(totalPrice)

def GetAddress(ligne):
    pattern1 = r"(?i)(?<=Address\s).*"
    match1 = re.search(pattern1,ligne)
    if match1:
        return(match1.group(0))
    pattern2 = r"\d{5}"
    match2 = re.search(pattern2,ligne)
    if match2:
        return ligne


def SimpleTreatments(text):
    name = ""
    date = ""
    destinator = ""
    email=""
    address=""
    Sales = []
    total = ""
    for ligne in text:
        tName = GetName(ligne)
        if tName:
            name = tName
        tDate = GetDate(ligne)
        if tDate:
            date = tDate
        tDest = GetDestinator(ligne)
        if tDest:
            destinator=tDest
        tTotal = GetTotal(ligne)
        if tTotal:
            total=tTotal
        sale = GetProductLigne(ligne)
        if sale:
            Sales.append(sale)
        tAddress = GetAddress(ligne)
        if tAddress:
            address+=" "+tAddress
        temail = GetEmail(ligne)
        if temail:
            email=temail
        
    facture = dbF.facture(name,date,destinator,email,address,Sales,total,None)
    return facture
    #return{"name":name,"date":date,"destinator":destinator,"Sales":Sales,"total":total}

#Prend en parametre des lignes extraite d'une zone de document et insere la data dans la facture
#Ecrase les valeurs unique
def ZoneAdd(text,facture:dbF.facture):
    for ligne in text:
        tName = GetName(ligne)
        if tName:
            facture.billName = tName
        tDate = GetDate(ligne)
        if tDate:
            facture.date = tDate
        tDest = GetDestinator(ligne)
        if tDest:
            facture.destinator=tDest
        tTotal = GetTotal(ligne)
        if tTotal:
            facture.pricetotal=tTotal
        sale = GetProductLigne(ligne)
        if sale:
            facture.productSales.append(sale)
        tAddress = GetAddress(ligne)
        if tAddress:
            facture.address+=" "+tAddress
        temail = GetEmail(ligne)
        if temail:
            facture.email=temail
        
#Prend en parametres une liste de zone traiter par OCR pour creer une facture unique a partir
def TraitementZone(listeZones,qrInf):
    facture = dbF.facture(billName="",date="",destinator="",email="",address="",productSales=[],pricetotal="",qrInfo=qrInf)
    for zone in listeZones:
        ZoneAdd(zone,facture)
    return facture
    
#Fait les validation possible a partir de la facture
def ValidateFacture(facture:dbF.facture):
    if(not facture.ValidateFullness()):
        return "Erfacture Non complete"
    if(not facture.validatePrice()):
        return "Erfacture pricenonEgale"
    if(not facture.validateQR()):
        return "Erfacture info non validé qrCode"
    return "Success"

def ConvertPrice(priceText:str):
    return int(priceText.replace(".",""))
        