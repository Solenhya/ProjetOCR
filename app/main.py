import services.downloadBill as dwldB
import services.dataBaseFormat as dbF
import services.OCRTesseract as OCRT
import services.OCRFormat as OCRF
import services.prétraitementImage as preImage
import services.qrCodeTraitement as QRT
from pathlib import Path
import os

from tqdm import tqdm
#Recupere la path complete d'un fichiers dans le dossier data
def GetFullPath(filename):
    current_directory = Path.cwd()
    # Define a relative path (relative to the current directory)
    relative_path = Path(f"data/{filename}")
    # Combine the current directory with the relative path
    full_path = current_directory / relative_path
    if(full_path.exists()):
        return full_path

#Fait le telechargements des fichier dans le dossier data
def TraiteDwldFactures():
    fileListe = os.listdir("data")
    manager = dbF.AZdbManager("fabien")
    manager.CreateTable()
    taille = len(fileListe)
    bloc=10
    traité = 0
    print(f"Traitement de {taille} fichiers de facture")
    errors =[]
    for i in tqdm(range(taille)):
        erreur = TraiteFacture(GetFullPath(fileListe[i]),manager,fileListe[i])
        if erreur:
            errors.append(erreur)
        traité+=1
        if(traité%bloc==0):
            tqdm.write(f"{traité}/{taille} fichiers traité")
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

if __name__ == "__main__":
    TraiteDwldFactures()
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