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
from .db import dataBaseManager,table_creation ,connection
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
from datetime import date

app = FastAPI(
    title="OCR Facture",
    description="A simple API for facture ocr",
    version="0.1.0"
)
templates = Jinja2Templates(directory="templates")
#Pour docker qui a une architecture un peu differentes
#templates = Jinja2Templates(directory="app/templates")
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


###Partie API 

#Partie Home et navigation
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

#Partie List
@app.get("/localfiles")
def GetAvailableFiles():
    data_path = GetPathToData()#Is created if not existing
    fileListe = os.listdir(data_path)
    return fileListe

@app.get("/users")
async def GetUsers(request : Request,token: Optional[str] = Cookie(None)):

    auth.get_current_user(token)#Renvoi une erreur qui est automatiquement traiter si l'authentification ne marche pas
    session = connection.get_session()
    users = userAccess.getAllUser(session)
    listDict = []
    for user in users:
        print(f"user todict : {user.ToDict()}")
        listDict.append(user.ToDict())
    session.close()
    return templates.TemplateResponse("users.html",{"request":request,"users":listDict})

@app.get("/uploadfile")
async def Upload(request : Request,token: Optional[str] = Cookie(None)):
    auth.get_current_user(token)
    return templates.TemplateResponse("uploadFile.html",{"request":request})

# Route to display the image after upload (without saving locally)
#Renvoyer le dictionnaire de requete en parametres pour que l'user le retransmette lors de l'insertion
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

app.post("/ValidateFacture")
async def validateFacture(request:Request):
    #Function pour valider la facture et dire ce qu'il manque va devoir gerer la mise en liste des sales qui ont été dérouler en sale1 sale2 ect
    #TODO
    pass


@app.post("/autoOCR")
async def autoOCR(request:Request,image: UploadFile =File(...),token: Optional[str] = Cookie(None)):
    user = auth.get_current_user(token)
    #Creer la session qui va servir tout du long de l'operation
    session = connection.get_session()
    print(f"Email : {user}")
    user = dataBaseManager.GetUserByEmail(session,user)
    print(f"User is : {user}")

    image_data = await image.read()
    if image_data:
        #Creer un dictionnaire préremplis pour suivre la requete
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
        #Fait du traitement de l'image pour l'ocr
        try:
            images , imageTime = measure_execution_time(preImage.GetImages,image, scaleFactor1=5, scaleFactor2=1, darkening=0.5)
        except:
            detail = "Erreur Serveur lors du traitement de l'image"
            HandleError(session,requestDict,"image",image,detail,500,origin="Distant",user=user)
        requestDict["image"]["status"]="Success"
        requestDict["image"]["time"]=imageTime
        #Fait l'ocr
        try:
            ocr , ocrTime =measure_execution_time(OCRT.OCRMultiple,images)
        except Exception as e:
            detail = f"Erreur Serveur lors de l'ocr {e}"
            HandleError(session,requestDict,"ocr",image,detail,500,origin="Distant",user=user)
        requestDict["ocr"]["status"]="Success"
        requestDict["ocr"]["time"]=ocrTime
        #Formate le text de l'ocr
        try:
            bill,formatTime = measure_execution_time(OCRF.TraitementZoneDict,ocr)
        except Exception as e:
            detail = f"Erreur Serveur lors du formatage : {e}"
            HandleError(session,requestDict,"formatage",image,detail,500,origin="Distant",user=user)
        
        #Valide la coherence de la facture
        erreurLocal = DoLocalValidation(image,dict=bill,qrC=qrC,origin="Distant")
        if (erreurLocal!=None) and (erreurLocal.gravity=="Error"):
            requestDict["formatage"]["status"]="Erreur"
            requestOCR = dbManager.CreateRequest(requestDict)
            dataBaseManager.EnterError(session,requestOCR,erreurLocal,user)
            session.close()
            raise HTTPException(status_code=422,detail="Erreur lors de la validation de la facture")
        requestDict["formatage"]["status"]="Success"
        requestDict["formatage"]["time"]=formatTime

        #Fait la validation de la facture comparativement au info de la base de donnée
        start_time = time.time()
        erreurDB = DoDataBaseValidation(image,bill,qrC,origin="Distant")
        if (erreurDB != None) and (erreurDB.gravity=="Error"):
            requestDict["db"]["status"]="Erreur"
            requestOCR = dbManager.CreateRequest(requestDict)
            dataBaseManager.EnterError(session,requestOCR,erreurDB,user)
            session.close()
            raise HTTPException(status_code=422,detail="Erreur la facture existe deja dans la base de donnée")
        
        #On creer les instance purrement objet
        facture = dbManager.CreateFacture(bill,qrC,"Distant",None)
        client = dbManager.CreateClient(session,bill,qrC)
        try:
            dataBaseManager.EnterFacture(session,facture,user,client)
        except:
            print("GROSS ERROR")
            #TODO Gere le cas ou on arrive pas a inserer la facture
            pass
        end_time = time.time()
        elapsed_time = end_time - start_time
        requestDict["db"]["status"]="Success"
        requestDict["db"]["time"]=elapsed_time
        tempsTotal = imageTime+ocrTime+QRTime+formatTime+elapsed_time
        requestDict["tempsTotal"]=tempsTotal

        #On rerécupere la facture pour y accoller la requete final
        requestOCR = dbManager.CreateRequest(requestDict)
        facture = dataBaseManager.GetFactureByName(session,bill["billName"])
        requestOCR.facture = facture
        #Si il y a des erreurs non bloquante on les rajoute
        erreurs = []
        if erreurLocal:
            erreurs.append(erreurLocal)
        if erreurDB:
            erreurs.append(erreurDB)
        requestOCR.saved_error=erreurs
        requestOCR.user=user
        session.add(requestOCR)
        session.commit()
        session.close()
        #Tout c'est bien passer on renvoie la page de resultat
        info={"result":"Facture uploader avec success"}
        return templates.TemplateResponse("uploadValidate.html",{"request":request,"info":info})

    return HTMLResponse(content="<h1>No image uploaded yet!</h1>")

# Image processing function extracted from autoOCR
async def process_image(image,user,session):
    #Creer un dictionnaire préremplis pour suivre la requete
    requestDict = dbManager.GetRequestDict()

    try:
        qrC ,QRTime = measure_execution_time(QRT.GetQRInfoDict,image)
    except:
            #TODO Bug sur la base de données rajouter la colone pour la lecture du QRCode
        raise HTTPException(status_code=422, detail="Erreur Serveur lors de la lecture du QRCode")  
        #Fait du traitement de l'image pour l'ocr
    try:
        images , imageTime = measure_execution_time(preImage.GetImages,image, scaleFactor1=5, scaleFactor2=1, darkening=0.5)
    except:
        detail = "Erreur Serveur lors du traitement de l'image"
        HandleError(session,requestDict,"image",image,detail,500,origin="Distant",user=user)
    requestDict["image"]["status"]="Success"
    requestDict["image"]["time"]=imageTime
        #Fait l'ocr
    try:
        ocr , ocrTime =measure_execution_time(OCRT.OCRMultiple,images)
    except Exception as e:
        detail = f"Erreur Serveur lors de l'ocr {e}"
        HandleError(session,requestDict,"ocr",image,detail,500,origin="Distant",user=user)
    requestDict["ocr"]["status"]="Success"
    requestDict["ocr"]["time"]=ocrTime
        #Formate le text de l'ocr
    try:
        bill,formatTime = measure_execution_time(OCRF.TraitementZoneDict,ocr)
    except Exception as e:
        detail = f"Erreur Serveur lors du formatage : {e}"
        HandleError(session,requestDict,"formatage",image,detail,500,origin="Distant",user=user)
    
    requestDict["formatage"]["status"]="Success"
    requestDict["formatage"]["time"]=formatTime
    timeToNow = formatTime+ocrTime+imageTime
    #Valide la coherence de la facture
    return {"bill":bill,"qrC":qrC,"requestDict":requestDict}


        
async def FinishProcess(bill,qrC,requestDict,session,user,previousTime):
    
    erreurLocal = DoLocalValidation(image,dict=bill,qrC=qrC,origin="Distant")
    if (erreurLocal!=None) and (erreurLocal.gravity=="Error"):
        requestDict["formatage"]["status"]="Erreur"
        requestOCR = dbManager.CreateRequest(requestDict)
        dataBaseManager.EnterError(session,requestOCR,erreurLocal,user)
        session.close()
        raise HTTPException(status_code=422,detail="Erreur lors de la validation de la facture")
    #Fait la validation de la facture comparativement au info de la base de donnée
    start_time = time.time()
    erreurDB = DoDataBaseValidation(image,bill,qrC,origin="Distant")
    if (erreurDB != None) and (erreurDB.gravity=="Error"):
        requestDict["db"]["status"]="Erreur"
        requestOCR = dbManager.CreateRequest(requestDict)
        dataBaseManager.EnterError(session,requestOCR,erreurDB,user)
        session.close()
        raise HTTPException(status_code=422,detail="Erreur la facture existe deja dans la base de donnée")
        
    #On creer les instance purrement objet
    facture = dbManager.CreateFacture(bill,qrC,"Distant",None)
    client = dbManager.CreateClient(session,bill,qrC)
    try:
        dataBaseManager.EnterFacture(session,facture,user,client)
    except:
        print("GROSS ERROR")
        #TODO Gere le cas ou on arrive pas a inserer la facture
        pass
    end_time = time.time()
    elapsed_time = end_time - start_time
    requestDict["db"]["status"]="Success"
    requestDict["db"]["time"]=elapsed_time
    tempsTotal = previousTime+elapsed_time
    requestDict["tempsTotal"]=tempsTotal
    #On rerécupere la facture pour y accoller la requete final
    requestOCR = dbManager.CreateRequest(requestDict)
    facture = dataBaseManager.GetFactureByName(session,bill["billName"])
    requestOCR.facture = facture
    #Si il y a des erreurs non bloquante on les rajoute
    erreurs = []
    if erreurLocal:
        erreurs.append(erreurLocal)
    if erreurDB:
        erreurs.append(erreurDB)
    requestOCR.saved_error=erreurs
    requestOCR.user=user
    session.add(requestOCR)
    session.commit()
    session.close()
    #Tout c'est bien passer on renvoie la page de resultat
    info={"result":"Facture uploader avec success"}
    return templates.TemplateResponse("uploadValidate.html",{"request":request,"info":info})#TODO


def DoLocalValidation(image,dict,qrC,origin,filename=None):
    validation = ValidateF.ValidateFacture(dict,qrC)
    if(validation!="Success"):
        message = f"Erreur {validation} dans la facture importer"
        if(origin!="Local"):
            saveas = saveError.SaveErrorImage(image)
        else:
            saveas = filename
        if validation=="Erfacture validationQR":
            gravity = "Warning"
        else:
            gravity = "Error"     
        erreur = dbManager.CreateError(gravity=gravity,result=message,origin=origin,savedAs=saveas)
        return erreur

def DoDataBaseValidation(image,dict,qrC,origin,filename=None):
    validation = dbManager.ValidateFacture(dict,qrC)
    if(validation["status"]!="Success"):
        message = f"Erreur {validation} dans la facture importer"
        if(origin!="Local"):
            saveas = saveError.SaveErrorImage(image)
        else:
            saveas = filename
        if validation=="Erreur Client":
            gravity = "Warning"
        else:
            gravity = "Error"     
        erreur = dbManager.CreateError(gravity=gravity,result=message,origin=origin,savedAs=saveas)
        return erreur


def HandleError(session,requestDict,keyStop,image,detail,statusCode,origin,user):
    saveLocation = saveError.SaveErrorImage(image)
    requestDict[keyStop]["status"]="Erreur"
    request = dbManager.CreateRequest(requestDict)
    erreur = dbManager.CreateError(gravity="Error",result=detail,origin=origin,savedAs=saveLocation)
    dataBaseManager.EnterError(session,request=request,erreur=erreur,user=user)
    session.close()
    raise HTTPException(status_code=statusCode, detail=detail)  


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

#Partie utilisateur

@app.get("/signUp")
async def Signup(request: Request):
    return templates.TemplateResponse("signUp.html",{"request":request})

@app.post("/createUser")
async def CreateUser(request: Request,userEmail:str = Form(...),userPassword:str = Form(...)):
    session = connection.get_session()
    user = userAccess.get_user(session,userEmail=userEmail)
    if user:
        raise HTTPException(status_code=409, detail="L'utilisateur existe deja")
    hashed = security.get_password_hash(userPassword)

    userAccess.save_user(userEmail,hashed)

@app.get("/login")
async def PageLogin(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.post("/login")
async def GetToken(request:Request,form_data: OAuth2PasswordRequestForm=Depends()):
    try:
        auth_value =await auth.login_for_access_token(form_data)
    except ValueError as e:
        return templates.TemplateResponse("error.html",{"request":request})
    response = RedirectResponse(url="/home", status_code=HTTP_303_SEE_OTHER)
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