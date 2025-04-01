from PIL import Image
import numpy as np


def ImageBrut(path):
    image = Image.open(path)
    return image

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

def Identity(image,parm1,parm2):
    return image

def GetImagesfromPath(path,scale1=20,scale2=4,imageUpgrade=Identity,par1=0,par2=0,sampling=Image.Resampling.NEAREST):
    resampling = Image.Resampling.LANCZOS
    image = Image.open(path)
    image_width, image_height = image.size

    width1 = image_width-500
    height1 = 160
    zone1 = (0,0,width1,height1)
    premiereImage = image.crop(zone1)
    premiereImage = premiereImage.resize((width1*scale1,height1*scale1),resample=sampling)
    #premiereImage = CutImage(premiereImage,180)

    height2 = image_height-height1
    width2 = image_width
    print(height2)
    zone2 = (0,height1,image_width,image_height)
    deuxiemeImage = image.crop(zone2)
    deuxiemeImage = deuxiemeImage.resize((width2*scale2,height2*scale2),resample=sampling)
    #Noircit les characters
    #deuxiemeImage = CutImage(deuxiemeImage,180)
    return [premiereImage,deuxiemeImage]

def GetImages(image,scaleFactor1=10,scaleFactor2=4,darkening=0.8,sampling=Image.Resampling.LANCZOS):
    if(type(image)==str):
        image = Image.open(image)
    images = CropImage(image)
    premierImage = images[0]
    premierImage = ScaleImage(premierImage,scaleFactor=scaleFactor1,sampling=sampling)
    secondeImage = images[1]
    secondeImage = ScaleImage(secondeImage,scaleFactor=scaleFactor2,sampling=sampling)
    if(darkening<1):
        premierImage = DarkenImage(premierImage,darkening=darkening)
        secondeImage = DarkenImage(secondeImage,darkening=darkening)
    return[premierImage,secondeImage]

def CropImage(image):
    image_width, image_height = image.size
    width1 = image_width-500
    height1 = 160
    zone1 = (0,0,width1,height1)
    premiereImage = image.crop(zone1)
    zone2 = (0,height1,image_width,image_height)
    deuxiemeImage = image.crop(zone2)
    return [premiereImage,deuxiemeImage]

def ScaleImage(image,scaleFactor,sampling):
    image_width, image_height = image.size
    image = image.resize((int(image_width*scaleFactor),int(image_height*scaleFactor)),resample=sampling)
    return image

def DarkenImage(image,darkening,threshold=240):
    #Convertit l'image en niveau de gris
    if image.mode != 'L':
        img_gray = image.convert('L')
    else:
        img_gray = image
    # Convertit en array numpy pour performance
    img_array = np.array(img_gray)
    # Creer un mask pour définir les pixel non blanc
    non_white_mask = img_array < threshold 
    # Fonce les pixel non blanc en multipliant par darkening <1
    img_array[non_white_mask] = np.clip(img_array[non_white_mask] * darkening, 0, 255).astype(np.uint8)  
    # reconvertit en image PIL
    img_enhanced = Image.fromarray(img_array)  
    return img_enhanced 