import app.services.downloadBill as dwldB
import app.services.dataBaseFormat as dbF
import app.services.OCRTesseract as OCRT
import app.services.OCRFormat as OCRF
import app.services.prétraitementImage as preImage
import app.services.qrCodeTraitement as QRT
from pathlib import Path
import os

from tqdm import tqdm

from fastapi import FastAPI

app = FastAPI(
    title="OCR Facture",
    description="A simple API for facture ocr",
    version="0.1.0"
)


def GetPathToData():  
    # Go up one folder (parent directory) and then into the 'data' folder
    parent_dir = os.path.dirname(os.getcwd())  # Get the parent directory of the current working directory
    data_dir = os.path.join(parent_dir, 'data')  # Path to the 'data' folder
    # Renvoi le chemin si le dossier existe
    if os.path.exists(data_dir) and os.path.isdir(data_dir):
        return data_dir


#Recupere la path complete d'un fichiers dans le dossier data
def GetFullPath(filename):
    data_directory = GetPathToData()
    full_path = os.path.join(data_directory, filename)
    if(os.path.exists(full_path)):
        return full_path
    print(f"erreur dans le chemin : {full_path}")

#Fait le telechargements des fichier dans le dossier data
def TraiteDwldFactures():
    data_path = GetPathToData()
    if data_path is None:
        raise FileNotFoundError("Data directory not found.")
    fileListe = os.listdir(data_path)
    
    manager = dbF.AZdbManager("fabien")
    manager.CreateTable()
    taille = len(fileListe)
    bloc=20
    traité = 0
    nbErreur=0
    print(f"Traitement de {taille} fichiers de facture")
    errors =[]
    for i in tqdm(range(taille)):
        erreur = TraiteFacture(GetFullPath(fileListe[i]),manager,fileListe[i])
        if erreur!="Success":
            errors.append(erreur)
            nbErreur+=1
        traité+=1
        if(traité%bloc==0):
            erreurpourc = (nbErreur/traité)*100
            tqdm.write(f"{traité}/{taille} fichiers traité avec un pourcentage d'erreur de {erreurpourc}% {nbErreur} et {traité}")
    with open("Erreurs.txt", "w") as file:
    # Write each message to the file with a newline
        file.writelines(f"{message}\n" for message in errors)
    manager.Disconnect()

def TraiteFacture(path,dbM,fileName):
    existingFacture = dbM.GetFactureDoc(fileName)
    if(len(existingFacture)>0):
        tqdm.write(f"Facture {fileName} deja scanner")
        return("Success")
    images = preImage.GetImages(path,scaleFactor1=5,scaleFactor2=1,darkening=0.5)
    ocr = OCRT.OCRMultiple(images)
    qrC = QRT.GetQRInfo(path)
    bill = OCRF.TraitementZoneDict(ocr)
    bill = dbF.facture.fromDict(bill)
    bill.qrInfo = qrC
    validation = OCRF.ValidateFacture(bill)
    if(validation!="Success"):
        message = f"Erreur {validation} dans la facture {fileName}"
        tqdm.write(message)
        return message
    result = dbM.ManageFacture(bill,fileName)
    if(result!="Success"):
        message = f"Erreur {result} dans la facture {fileName}"
        tqdm.write(message)
        return message
    return "Success"

#Partie API 
@app.get("/GetAvailableFiles")
def GetAvailableFiles():
    data_path = GetPathToData()
    if data_path is None:
        raise FileNotFoundError("Data directory not found.")
    fileListe = os.listdir(data_path)
    return fileListe

@app.post("/ocrBrutInfo")
def ocrBrutFacture(fileName):
    fullPath = GetFullPath(fileName)
    image = preImage.ImageBrut(fullPath)
    images = preImage.GetImages(fullPath)
    ocr = OCRT.OCRMultiple(images)
    qrC = QRT.GetQRInfo(fullPath)
    return{"ocr":ocr,"qr":qrC}

@app.post("/ocrValidate")
def ocrValidate(fileName):
    info = ocrBrutFacture(fileName)
    ocrFormat = OCRF.TraitementZoneDict(info["ocr"])
    qrC = info["qr"]
    bill = dbF.facture.fromDict(ocrFormat)
    bill.qrInfo = qrC
    IntraValidation = OCRF.ValidateFactureComplete(bill)
    manager = dbF.AZdbManager("fabien")
    dbValidation = manager.DataBaseValidation(bill,fileName)
    manager.Disconnect()
    return {"IntraValidation":IntraValidation,"dbValidation":dbValidation}

@app.post("/ocrFactureName")
def ocrFactureName(fileName):
    fullPath = GetFullPath(fileName)
    manager = dbF.AZdbManager("fabien")
    result = TraiteFacture(fullPath,manager,fileName)
    manager.Disconnect()
    return result

if __name__ == "__main__":
    try:
        TraiteDwldFactures()
    except Exception as e:
        print(f"Erreur dans le traitement {e}")
    """
    path = GetFullPath("FAC_2018_0001-654.png")
    manager = dbF.AZdbManager("fabien")
    TraiteFacture()
    
    """
    """
    images = preImage.GetImagesfromPath(path)
    ocr = OCRT.OCRMultiple(images)
    for oc in ocr:
        print(f"OC : {oc}")
    qrC = QRT.GetQRInfo(path)
    bill = OCRF.TraitementZone(ocr,qrC)
    validation=OCRF.ValidateFacture(bill)
    print(validation)
    manager.Disconnect()"
    """