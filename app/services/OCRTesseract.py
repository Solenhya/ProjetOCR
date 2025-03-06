import pytesseract

def OCRFile():
    pass

def OCRPath(path):
    text = pytesseract.image_to_string(path,config='--psm 6')
    return text.split('\n')