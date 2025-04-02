from app.services import prétraitementImage,OCRTesseract,OCRFormat
import pytest
import time
import json

def load_test_data():
    with open('testdata.json', 'r') as file:
        data = json.load(file)  # Load the JSON data into a Python object
    return data


@pytest.mark.parametrize("test_case", load_test_data())
def testCustomParam(test_case):
    path = test_case["path"]
    images = prétraitementImage.GetImages(path,scaleFactor1=5,scaleFactor2=1,darkening=0.5)
    zones = OCRTesseract.OCRMultiple(images)
    formated = OCRFormat.TraitementZoneDict(zones)
    expectedResult = test_case["expectedResult"]
    assert formated["billName"]==expectedResult["billName"]
    assert formated["date"]==expectedResult["date"]
    assert formated["destinator"]==expectedResult["destinator"]
    assert formated["email"]==expectedResult["email"]
    assert formated["address"]==expectedResult["address"]
    assert len(formated["productSales"])==len(expectedResult["sales"])

    for i in range(len(formated["productSales"])):
        assert formated["productSales"][i]["productName"]==expectedResult["sales"][i]["name"]
        assert formated["productSales"][i]["productQuant"]==expectedResult["sales"][i]["quantity"]
        assert formated["productSales"][i]["productPrice"]==expectedResult["sales"][i]["price"]

"""
def testall(path,result):
    images = prétraitementImage.GetImages(path)
    zones = OCRTesseract.OCRMultiple(images)
    formated = OCRFormat.TraitementZoneDict(zones)
    print(formated)

if __name__ =="__main__":
    timeBefore = time.time()
    testall("FAC_2018_0001-654.png","bla")
    timeAfter = time.time()
    print(f"Temps requis {timeAfter-timeBefore}")
"""