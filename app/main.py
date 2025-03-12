import services.downloadBill as dwldB
import services.dataBaseFormat as dbF
import services.OCRTesseract as OCRT
import services.OCRFormat as OCRF
import services.prétraitementImage as preImage
import services.qrCodeTraitement as QRT
from pathlib import Path
import os


def GetFullPath(filename):
    current_directory = Path.cwd()

    # Define a relative path (relative to the current directory)
    relative_path = Path(f"data/{filename}")
    # Combine the current directory with the relative path
    full_path = current_directory / relative_path
    if(full_path.exists()):
        return full_path

def TraiteDwldFactures():
    fileListe = os.listdir("data")
    manager = dbF.AZdbManager("fabien")
    manager.CreateTable()
    taille = len(fileListe)
    bloc=10
    traité = 0
    print(f"Traitement de {taille} fichiers de facture")
    errors =[]
    for i in range(taille):
        erreur = TraiteFacture(GetFullPath(fileListe[i]),manager,fileListe[i])
        if erreur:
            errors.append(erreur)
        traité+=1
        if(traité%bloc==0):
            print(f"{traité}/{taille} fichiers traité")
    with open("Erreurs.txt", "w") as file:
    # Write each message to the file with a newline
        file.writelines(f"{message}\n" for message in errors)
    manager.Disconnect()

def TraiteFacture(path,dbM,fileName):
    image = preImage.ImagefromPath(path)
    ocr = OCRT.OCRFrom(image)
    bill = OCRF.SimpleTreatments(ocr)
    qr = QRT.GetQRInfo(path)
    bill.qrInfo=qr
    result = dbM.ManageFacture(bill)
    if(result!="Success"):
        message = f"Erreur {result} dans la facture {fileName}"
        print(message)
        return message

#TraiteDwldFactures()
testTO = GetFullPath("FAC_2019_0041-875.png")
manager = dbF.AZdbManager("fabien")
TraiteFacture(testTO,manager,"FAC_2019_0041-875.png")
manager.Disconnect()