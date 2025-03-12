from PIL import Image

def ImagefromPath(path):
    image = Image.open(path)
    # Get the size of the image
    image_width, image_height = image.size
    # Defini la taille du carrer que l'on souhaite masker
    height = 150  
    width = 300
    # Defini le coin haut gauche et bas droit de la zone a traiter
    zone = (image_width - width, 0, image_width, height)
    # Creer l'image blanche qui va écraser
    white_image = Image.new("RGB", (zone[2] - zone[0], zone[3] - zone[1]), (255, 255, 255))
    # Ecrase la region defini par un carrer blanc
    image.paste(white_image, zone)   
    return image

def GetImagesfromPath(path,scale1=10,scale2=4):
    image = Image.open(path)
    image_width, image_height = image.size
    width1 = image_width-500
    height1 = 160
    zone1 = (0,0,width1,height1)
    premiereImage = image.crop(zone1)
    premiereImage = premiereImage.resize((width1*scale1,height1*scale1))

    height2 = image_height-height1
    width2 = image_width
    zone2 = (0,height1,image_height,image_width)
    deuxiemeImage = image.crop(zone2)
    deuxiemeImage = deuxiemeImage.resize((width2*scale2,height2*scale2))
    return [premiereImage,deuxiemeImage]
