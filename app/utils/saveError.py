import os
import sys

import uuid
from datetime import datetime
from PIL import Image


#This is a function that create a name and verify it doesn't already exist (uuid mean that it won't happen)
def CreateFileName():
    # Get the current time (day and hour)
    current_time = datetime.now()
    # Format the time as 'YYYYMMDD_HH' (Day and Hour)
    formatted_time = current_time.strftime("%Y%m%d_%H")
    # Generate a random UUID
    unique_id = uuid.uuid4()
    # Combine the formatted time and UUID
    fileName = f"{formatted_time}_{unique_id}.png"
    return fileName

#A Function to set up (if it doesn't exist)and return the path to the folder where we keep the file that presented error
def GetFolderPath():
    folderPath = "errorFile"
    if not os.path.isdir(folderPath):
        os.makedirs(folderPath)
        print(f"Folder d'erreur creer")
    return folderPath

#A Function to save an image into the errorFolder with an unique name
def SaveErrorImage(image):
    folderPath = GetFolderPath()
    fileName = CreateFileName()
    saveLocation = os.path.join(folderPath,fileName)
    image.save(saveLocation)
    print(f"Image saved at {saveLocation}")
    return fileName

def LoadErrorImage(imageName):
    saveLocation = os.path.join(GetFolderPath(),imageName)
    if os.path.exists(saveLocation):
        try:
            image = Image.open(saveLocation)
        except:
            print(f"Erreur lors de la lecture de l'image a l'emplacement {saveLocation}")
            return None