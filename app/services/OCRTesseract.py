import pytesseract


def OCRFrom(path):
    text = pytesseract.image_to_string(path,config='--psm 6 --oem 1')
    return text.split('\n')

def OCRMultiple(listImage):
    retour = []
    for image in listImage:
        text = pytesseract.image_to_string(image,config='--psm 6 --oem 1')
        text = text.split("\n")
        retour.append(text)
    return retour