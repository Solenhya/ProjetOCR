import os 
from dotenv import load_dotenv

class productSale:
    def __init__(self,quantity,price,name):
        self.quantity = quantity
        self.price = price
        self.name = name
    
    def getTotalCost(self):
        return self.quantity*self.price
    
class facture:
    def __init__(self,billName,date,destinator,address,productSales,pricetotal):
        self.billName = billName
        self.date = date
        self.destinator = destinator
        self.address = address
        self.productSales = productSales
        self.pricetotal = pricetotal

    def validatePrice(self):
        suposePrice = 0
        for sale in self.productSales:
            suposePrice+=sale.getTotalCost()
        priceDiff = self.pricetotal-suposePrice
        if(priceDiff>0):
            return False
        return True
    
    def validateAddress(self):
        #TODO
        return True
    
class DataBaseManager:

    def __init__(self):
        #TODO
        pass

    def CreateTable(self):
        #TODO
        pass