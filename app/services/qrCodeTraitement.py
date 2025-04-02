from pyzbar.pyzbar import decode
from PIL import Image
import re

# Function to parse the data into a dictionary
def parse_qr_data(qr_data):
    # Split the QR data by newlines to get each key-value pair
    data_dict = {}
    lines = qr_data.split("\n")
    
    for line in lines:
        # Split each line by the first colon
        if ":" in line:
            key, value = line.split(":", 1)
            data_dict[key.strip()] = value.strip()  # Store it in dictionary
    return data_dict

def GetQRData(image):
    #Si on a donner un string on doit load l'image
    if(type(image)==str):
        image = Image.open(image)
    code = decode(image)
    if(len(code)>0):
        decoded_data = code[0].data.decode('utf-8')
        return parse_qr_data(decoded_data)
    return None

def GetQRInfoDict(imagePath):
    data = GetQRData(imagePath)

    if data:
        values = {"facName":data["INVOICE"],"facDate":data["DATE"],"custBirth":"","custGender":data["CUST"][0]}
        ligne = data["CUST"]
        reg = r"(?<=birth\s).+"
        match = re.search(reg,ligne)
        values["custBirth"]=match.group(0)
        return values
"""
INVOICE:FAC/2018/0001
DATE:2018-10-13 03:27:0
CUST:F, birth 2000-02-16

"""