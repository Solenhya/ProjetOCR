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
    for i in range(taille):
        TraiteFacture(GetFullPath(fileListe[i]),manager)
        traité+=1
        if(traité%bloc==0):
            print(f"{traité}/{taille} fichiers traité")
    manager.Disconnect()

def TraiteFacture(path,dbM):
    image = preImage.ImagefromPath(path)
    ocr = OCRT.OCRFrom(image)
    bill = OCRF.SimpleTreatments(ocr)
    qr = QRT.GetQRInfo(path)
    bill.qrInfo=qr
    dbM.ManageFacture(bill)

TraiteDwldFactures()