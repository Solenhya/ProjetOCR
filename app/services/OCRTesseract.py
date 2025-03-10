import pytesseract


def OCRFrom(path):
    text = pytesseract.image_to_string(path,config='--psm 6')
    return text.split('\n')