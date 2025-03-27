import re
from tqdm import tqdm
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
        patternText = r"(.*)(\d+)\s*x\s*([0-9.,]+)"
        match = re.search(patternText, ligne)
        productPrice = ConvertPrice(match.group(3))
        productQuant = int(match.group(2))
        return {"productName":match.group(1).rstrip(),"productQuant":int(match.group(2)),"productPrice":productPrice}



def GetEmail(ligne):
    #Pattern d'email avec de la flexibilité pour les espace blanc
    pattern = r"Email\s+(.*?)$"
    match = re.search(pattern,ligne)
    if match:
        email_with_spaces = match.group(1)  # "xdk f@dsds .sds"
        # Now remove all whitespace
        email_no_spaces = re.sub(r"\s+", "", email_with_spaces)  # "xdkf@dsds.sds"
        return(email_no_spaces)

def GetDestinator(ligne):
    pattern = r"(?<=Bill to\s).+"
    match = re.search(pattern,ligne)
    if match:
        return(match.group(0))

def GetTotal(ligne):
    pattern = r"(?i)(?<=Total\s)[0-9.,]+"
    match = re.search(pattern,ligne)
    if match:

        totalPrice = ConvertPrice(match.group(0))
        print(f"totalFound : {match.group(0)} convert to {totalPrice}")
        return(totalPrice)

def GetAddress(ligne):
    pattern1 = r"(?i)address\s+(.*)"
    match1 = re.search(pattern1,ligne)
    if match1:
        return(match1.group(1))
    pattern2 = r"\d{5}"
    match2 = re.search(pattern2,ligne)
    if match2:
        return ligne

def ZoneAddDict(text,dict):
    for ligne in text:
        tName = GetName(ligne)
        if tName:
            dict["billName"] = tName
        tDate = GetDate(ligne)
        if tDate:
            dict["date"] = tDate
        tDest = GetDestinator(ligne)
        if tDest:
            dict["destinator"]=tDest
        tTotal = GetTotal(ligne)
        if tTotal:
            dict["pricetotal"]=tTotal
        sale = GetProductLigne(ligne,dict=True)
        if sale:
            dict["productSales"].append(sale)
        tAddress = GetAddress(ligne)
        if tAddress:
            #Si on est a la premiere ligne on l'insert directement sinon on mets un espace entre
            if(dict["address"]==""):
                dict["address"]+=tAddress
            else:
                dict["address"]+=" "+tAddress
        temail = GetEmail(ligne)
        if temail:
            dict["email"]=temail


def TraitementZoneDict(listeZones):
    retour = {"billName":"","date":"","destinator":"","email":"","address":"","productSales":[],"pricetotal":""}
    for zone in listeZones:
        ZoneAddDict(zone,retour)
    return retour

def ConvertPrice(priceText:str):
    # Trouve tout les chiffres pour retirer la virgule
    numbers = re.findall(r'\d+', priceText)
    # Concatene
    result = ''.join(numbers)
    #print(f"brut {priceText} result {result} conversion {int(result)}")
    return int(result)
        