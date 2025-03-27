from .services import downloadBill as dwldB
from .services import OCRTesseract as OCRT
from .services import OCRFormat as OCRF
from .services import prétraitementImage as preImage
from .services import qrCodeTraitement as QRT
from .services import ValidateFacture as ValidateF
from pathlib import Path
import os
#Call load dotenv avant d'en avoir besoin
from dotenv import load_dotenv
load_dotenv()
from .db import dataBaseManager,table_creation
import time
from PIL import Image

from tqdm import tqdm

from fastapi import FastAPI , Request , File , UploadFile , Form ,Cookie ,Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_303_SEE_OTHER
import io
import base64

from .utils import jinjaTranslation
from .utils.imageEncoding import convertImageB64
from .utils.executionTime import measure_execution_time
from .utils import saveError
from .userManagement import auth,security , userAccess

from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="OCR Facture",
    description="A simple API for facture ocr",
    version="0.1.0"
)
#templates = Jinja2Templates(directory="templates")
#Pour docker qui a une architecture un peu differentes
templates = Jinja2Templates(directory="app/templates")
static_dir = "static"
if not os.path.isdir(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory="static"), name="static")
dbManager = dataBaseManager.DBManager()


def SaveImageToError(image):
    pass #TODO implementer le systeme de sauvegarde de l'image

def GetPathToData():  
    # Go up one folder (parent directory) and then into the 'data' folder
    parent_dir = os.path.dirname(os.getcwd())  # Get the parent directory of the current working directory
    data_dir = os.path.join(parent_dir, 'data')  # Path to the 'data' folder
    # Renvoi le chemin si le dossier existe
    if os.path.exists(data_dir) and os.path.isdir(data_dir):
        return data_dir
    else:
        os.makedirs(data_dir)
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
    
    #manager = dbF.AZdbManager("fabien")
    #manager.CreateTable()
    taille = len(fileListe)
    bloc=20
    traité = 0
    nbErreur=0
    print(f"Traitement de {taille} fichiers de facture")
    errors =[]
    for i in tqdm(range(taille)):
        erreur = ""#TraiteFacture(GetFullPath(fileListe[i]),manager,fileListe[i]) TODO REfacto
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
    #manager.Disconnect()

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


#Partie API 

@app.get("/")
async def homePage(request : Request,token: Optional[str] = Cookie(None)):
    print(token)
    if not token:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    user = auth.get_current_user(token)
    return templates.TemplateResponse("uploadFile.html", {"request": request, "user": user})

@app.get("/home")
async def ConnectedHome(request : Request,token: Optional[str]=Cookie(None)):
    auth.get_current_user(token)
    return templates.TemplateResponse("accueil.html",{"request":request})

@app.get("/list")
async def HomeList(request : Request,token:Optional[str]=Cookie(None)):
    auth.get_current_user(token)
    return templates.TemplateResponse("accueilListe.html",{"request":request})

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
async def GetUsers(request : Request,token: Optional[str] = Cookie(None)):
    #TODO set users from dataBase
    auth.get_current_user(token)#Renvoi une erreur qui est automatiquement traiter si l'authentification ne marche pas
    users = userAccess.getAllUser()
    listDict = []
    for user in users:
        print(f"user todict : {user.ToDict()}")
        listDict.append(user.ToDict())
    return templates.TemplateResponse("users.html",{"request":request,"users":listDict})

@app.get("/uploadfile")
async def Upload(request : Request,token: Optional[str] = Cookie(None)):
    auth.get_current_user(token)
    return templates.TemplateResponse("uploadFile.html",{"request":request})

# Route to display the image after upload (without saving locally)
@app.post("/display-ocr", response_class=HTMLResponse)
async def display_image(request: Request,image: UploadFile =File(...),token: Optional[str] = Cookie(None)):
    # Get the image data from the request state
    auth.get_current_user(token)
    image_data = await image.read()
    
    if image_data:
        # Convert the image to base64 so it can be displayed in an <img> tag in HTML
        image = Image.open(io.BytesIO(image_data))
        images = preImage.GetImages(image=image,scaleFactor1=imageParam["scaleFactor1"],scaleFactor2=imageParam["scaleFactor2"],darkening=imageParam["darkening"])
        ocrInfo=[]
        osd = OCRT.OCRWithBoxe(images)
        for part in osd:
            ajout = {}
            ajout["text"]=part["text"]
            ajout["image"]=convertImageB64(part["imageBoxe"])
            ajout["descrption"]="Image de l'OSD"
            ocrInfo.append(ajout)
        originalImage=convertImageB64(image)
        ocr = []
        for part in osd:
            ocr.append(part["text"])
        format = OCRF.TraitementZoneDict(ocr)
        elements=jinjaTranslation.GetInfo(format)

        return templates.TemplateResponse("showOCR.html",{"request":request,"ocrInfo":ocrInfo,"originalImage":originalImage,"elements":elements})

    return HTMLResponse(content="<h1>No image uploaded yet!</h1>")



@app.post("/autoOCR")
async def autoOCR(request:Request,image: UploadFile =File(...),token: Optional[str] = Cookie(None)):
    auth.get_current_user(token)
    image_data = await image.read()
    #TODO Implement error 400 for bad image and bad QRCode
    if image_data:
        requestDict = dbManager.GetRequestDict()
        try:
            image = Image.open(io.BytesIO(image_data))
        except:
            raise HTTPException(status_code=422,detail="Impossible de lire l'image")
        try:
            qrC ,QRTime = measure_execution_time(QRT.GetQRInfoDict,image)
        except:
            #TODO Bug sur la base de données rajouter la colone pour la lecture du QRCode
            raise HTTPException(status_code=422, detail="Erreur Serveur lors de la lecture du QRCode")  
        try:
            images , imageTime = measure_execution_time(preImage.GetImages,image, scaleFactor1=5, scaleFactor2=1, darkening=0.5)
        except:
            saveLocation = saveError.SaveErrorImage(image)
            requestDict["image"]["status"]="Erreur"
            raise HTTPException(status_code=500, detail="Erreur Serveur lors du traitement de l'image")
        requestDict["image"]["status"]="Success"
        requestDict["image"]["time"]=imageTime
        try:
            ocr , ocrTime =measure_execution_time(OCRT.OCRMultiple,images)
        except:
            requestDict["ocr"]["status"]="Erreur"
            raise HTTPException(status_code=500, detail="Erreur Serveur lors de l'ocr")  
        requestDict["ocr"]["status"]="Success"
        requestDict["ocr"]["time"]=ocrTime

        bill,formatTime = measure_execution_time(OCRF.TraitementZoneDict,ocr)


        erreur = DoValidation(image,dict=bill,qrC=qrC,origin="Distant")
        #TODO save l'erreur si elle existe bloquer le process si c'est trop grave et continuer avec la validation coter base de donnée



        tempsTotal = imageTime+ocrTime+QRTime+formatTime
        


    return HTMLResponse(content="<h1>No image uploaded yet!</h1>")
    
def DoValidation(image,dict,qrC,origin,filename=None):
    validation = ValidateF.ValidateFacture(dict,qrC)
    if(validation!="Success"):
        message = f"Erreur {validation} dans la facture importer"
        if(origin!="Local"):
            saveas = SaveImageToError(image)
        else:
            saveas = filename
        imageName = SaveImageToError(image)
        if validation=="Erfacture validationQR":
            gravity = "Warning"
        else:
            gravity = "Error"     
        erreur = dbManager.CreateError(gravity=gravity,result=message,origin=origin,savedAs=saveas)
        return erreur
       


@app.post("/resultat")
async def result(request:Request,facture,ocr):
    validation=ValidateF.ValidateFacture(facture,ocr)
    if(validation=="Succes"):
        status="K"
    else:
        pass
    status = "K"
    return templates.TemplateResponse("uploadValidate.html",{"request":request,"info":{"result":status}})

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

#Partie utilisateur

@app.get("/signUp")
async def Signup(request: Request):
    return templates.TemplateResponse("signUp.html",{"request":request})

@app.post("/createUser")
async def CreateUser(request: Request,userEmail:str = Form(...),userPassword:str = Form(...)):
    user = userAccess.get_user(userEmail=userEmail)
    if user:
        raise HTTPException(status_code=409, detail="L'utilisateur existe deja")
    hashed = security.get_password_hash(userPassword)
    userAccess.save_user(userEmail,hashed)
    #TODO changer ça
    return{"usermail":userEmail,"password":hashed}

@app.get("/login")
async def PageLogin(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.post("/login")
async def GetToken(request:Request,form_data: OAuth2PasswordRequestForm=Depends()):
    try:
        auth_value =await auth.login_for_access_token(form_data)
    except ValueError as e:
        return templates.TemplateResponse("error.html",{"request":request})
    response = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    response.set_cookie(key="token", value=auth_value["access_token"])
    return response

@app.get("/disconnect")
async def disconnect(request : Request):
    response = RedirectResponse(url="/login",status_code=HTTP_303_SEE_OTHER)
    response.delete_cookie(key="token")
    return response

#Partie erreur

# Custom exception handler for HTTPException
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Extract status code and detail from the exception
    return templates.TemplateResponse("error.html", {
        "request": request,
        "status_code": exc.status_code,
        "detail": exc.detail
    })


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