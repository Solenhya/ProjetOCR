
def TranslateInputType(value):
            # Determine the input type based on the value type
        if isinstance(value, str):
            input_type = "text"
        elif isinstance(value, int):
            input_type = "number"
        elif isinstance(value, float):
            input_type = "number"
        elif isinstance(value, bool):
            input_type = "checkbox"
        elif isinstance(value, str) and "-" in value:  # assuming it's a date string like 'YYYY-MM-DD'
            input_type = "date"
        else:
            input_type = "text"  # Default fallback
        return input_type


def GetInfo(format):
    """
    Prend un ocr d'une facture et renvoie des elements a display par jinja
    """
    elements = []
    for key,value in format.items():
        if(key=="productSales"):
            elementFormat = "List"
            elementList=[]
            index = 0
            for sale in value:
                ajout = sale
                sale["index"]=index
                elementList.append(sale)
                index+=1
            element = {"format":elementFormat,"liste":elementList}
        else:
            elementFormat="single"
            element = {"name":key,"value":value,"type":TranslateInputType(value),"format":elementFormat}
        elements.append(element)
    for element in elements:
        print(f"Element : {element}")
    return elements
