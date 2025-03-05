import xml.etree.ElementTree as ET
import requests
import os 
from dotenv import load_dotenv
import xml.etree.ElementTree as ET


def getListRequest(requete):
    host = os.getenv("LIST_HOST")
    sign = os.getenv("LIST_AUTH")
    return requests.get(f"https://{host}/{requete}?restype=container&comp=list&{sign}")

def getImageRequest(requete,origin):
    host = os.getenv("LIST_HOST")
    sign = os.getenv("LIST_AUTH")
    return requests.get(f"https://{host}/{origin}/{requete}?{sign}")

def extract_blob_names(xml_string):
    # Parse the XML string
    root = ET.fromstring(xml_string)
    # Find all Blob elements
    blobs = root.findall('.//Blob')
    # Extract names of blobs
    blob_names = [blob.find('Name').text for blob in blobs]
    return blob_names

def DowloadImages(filepath,date,count=10):
    origine = f"invoices-{date}"
    requestList = getListRequest(origine)
    if(requestList.status_code!=200):
        return
        #TODO
    listeFile = extract_blob_names(requestList.text)
    downloadcount = 0
    totalDownload = len(listeFile)
    print(f"Télechargement de {totalDownload} fichiers pour {date}")
    for file in listeFile:
        request = getImageRequest(file,origine)
        if(request.status_code==200):
            finalpath = os.path.join(filepath,file)
            with open(finalpath, "wb") as file:
                file.write(request.content)
            downloadcount+=1
        else:
            print(f"Erreur {request.status_code} lors du telechargement du fichier {file}")

        if(downloadcount%count==0):
            print(f"Telecharger {downloadcount} fichier sur {totalDownload}")
    print(f"Fini de télécharger tout les fichier pour {date}")
    return downloadcount
if __name__=="__main__":
    load_dotenv()
    availableDate = [2018,2019,2020,2021,2022,2023,2024,2025]
    for date in availableDate:
        DowloadImages("test",date)
