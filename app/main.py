import app.services.downloadBill as dwldB
import app.services.dataBaseFormat as dbF
import app.services.OCRTesseract as OCRT
import app.services.OCRFormat as OCRF
import app.services.prétraitementImage as preImage
import app.services.qrCodeTraitement as QRT
import app.services.ValidateFacture as ValidateF
from pathlib import Path
import os
#Call load dotenv avant d'en avoir besoin
from dotenv import load_dotenv
load_dotenv()
from app.db import dataBaseManager,table_creation
import time
from PIL import Image

from tqdm import tqdm

from fastapi import FastAPI , Request , File , UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,HTMLResponse
import io
import base64

app = FastAPI(
    title="OCR Facture",
    description="A simple API for facture ocr",
    version="0.1.0"
)
templates = Jinja2Templates(directory="templates")

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

def measure_execution_time(func, *args, **kwargs):
    """
    Measures the execution time of a function.
    
    Parameters:
    - func: The function to be timed.
    - *args: Positional arguments for the function.
    - **kwargs: Keyword arguments for the function.
    
    Returns:
    - result: The result of the function call.
    - elapsed_time: Time in seconds that the function took to execute.
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    return result, elapsed_time

imageParam = {"scaleFactor1":5,"scaleFactor2":1,"darkening":0.5}

def TraiteFactureFile(file,origin,fileName,user,manager=None):
    if(not manager):
        manager = dataBaseManager.DBManager() 
    images , imageTime = measure_execution_time(preImage.GetImages,file, scaleFactor1=5, scaleFactor2=1, darkening=0.5)
    ocr , ocrTime =measure_execution_time(OCRT.OCRMultiple,images)  
    qrC ,QRTime = measure_execution_time(QRT.GetQRInfoDict,file)
    bill,formatTime = measure_execution_time(OCRF.TraitementZoneDict,ocr)

    validation = ValidateF.ValidateFacture(bill,qrC)
    if(validation!="Success"):
        message = f"Erreur {validation} dans la facture {fileName}"
        tqdm.write(message)
        return message
    
    #TODO validation coter base de donnée
    manager.CreateEntriesFacture(bill,qrC,origin,fileName,user)
    return "Success"

def convertImageB64(image):
        # Convert the image to a BytesIO object
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)  # Go to the beginning of the BytesIO stream

    # Convert the BytesIO object to a Base64 string
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
    return img_base64

#Partie API 
@app.get("/GetAvailableFiles")
def GetAvailableFiles():
    data_path = GetPathToData()
    if data_path is None:
        raise FileNotFoundError("Data directory not found.")
    fileListe = os.listdir(data_path)
    return fileListe

users = [
    {"id": 1, "userEmail": "user1@example.com", "userName": "User One", "userPassword": "password123","permissions":"Read"},
    {"id": 2, "userEmail": "user2@example.com", "userName": "User Two", "userPassword": "password456","permissions":"Read/Upload"},
    {"id": 3, "userEmail": "user3@example.com", "userName": "User Three", "userPassword": "password789","permissions":"All"},
]

@app.get("/users")
def GetUsers(request : Request):
    #TODO set users from dataBase
    return templates.TemplateResponse("users.html",{"request":request,"users":users})

@app.get("/uploadfile")
def Upload(request : Request):
    return templates.TemplateResponse("uploadFile.html",{"request":request})

# Route to handle the image upload with redirection
@app.post("/uploadfile")
async def upload_file(request: Request, image: UploadFile = File(...)):
    # Read the image data into memory
    image_data = await image.read()
    # Store the image data in a session or temporary variable (e.g., request state)
    request.state.image_data = image_data  # Store image data in the request object for this session
    # After processing, redirect to the display-image endpoint
    return RedirectResponse(url="/display-image", status_code=303)

# Route to display the image after upload (without saving locally)
@app.post("/display-ocr", response_class=HTMLResponse)
async def display_image(request: Request,image: UploadFile =File(...)):
    # Get the image data from the request state
    image_data = await image.read()
    
    if image_data:
        # Convert the image to base64 so it can be displayed in an <img> tag in HTML
        image = Image.open(io.BytesIO(image_data))
        images = preImage.GetImages(image=image,scaleFactor1=imageParam["scaleFactor1"],scaleFactor2=imageParam["scaleFactor2"],darkening=imageParam["darkening"])
        ocrInfo=[]
        osd = OCRT.OCRWithBoxe(images)
        for ocr in osd:
            ajout = {}
            ajout["text"]=ocr["text"]
            ajout["image"]=convertImageB64(ocr["imageBoxe"])
            ajout["descrption"]="Image de l'OSD"
            ocrInfo.append(ajout)
        img_str=convertImageB64(image)
        return templates.TemplateResponse("showOCR.html",{"request":request,"ocrInfo":ocrInfo})
        # Return the HTML with the image embedded as base64
        html_content = f'''
        <html>
            <body>
                <h1>Uploaded Image</h1>
                <img src="data:image/png;base64,{img_str}" alt="Uploaded Image"/>
            </body>
        </html>
        '''
        return HTMLResponse(content=html_content)

    return HTMLResponse(content="<h1>No image uploaded yet!</h1>")

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
    table_creation.DeleteTable()
    table_creation.CreateTable()
    image = Image.open(GetFullPath("FAC_2018_0001-654.png"))
    TraiteFactureFile(image,"Local","FAC_2018_0001-654.png",1)
    print("Succes")
    """
    try:
        TraiteDwldFactures()
    except Exception as e:
        print(f"Erreur dans le traitement {e}")

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