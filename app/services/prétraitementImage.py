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

def GetImagesFull(path):
    scale1 = 10
    scale2 = 4
    boostThresh = 200
    boostValue = 30
    resampling = Image.Resampling.LANCZOS
    
    image = Image.open(path)
    image_width, image_height = image.size
    width1 = image_width-500
    height1 = 160
    zone1 = (0,0,width1,height1)
    premiereImage = image.crop(zone1)
    premiereImage = premiereImage.resize((width1*scale1,height1*scale1),resample=resampling)
    premiereImage = ShiftImage(premiereImage,boostThresh,boostValue)

    height2 = image_height-height1
    width2 = image_width
    zone2 = (0,height1,image_width,image_height)
    deuxiemeImage = image.crop(zone2)
    deuxiemeImage = deuxiemeImage.resize((width2*scale2,height2*scale2),resample=resampling)
    deuxiemeImage = ShiftImage(deuxiemeImage,boostThresh,boostValue)

    return [premiereImage,deuxiemeImage]

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

def GetImages(path,scaleFactor1=10,scaleFactor2=4,darkening=0.8,sampling=Image.Resampling.LANCZOS):
    image = Image.open(path)
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
    if image.mode != 'L':
        img_gray = image.convert('L')
    else:
        img_gray = image
    # Convert to numpy array for easier manipulation
    img_array = np.array(img_gray)
    # Create a mask for non-white pixels (adjust threshold as needed)
    # Pixels with values less than threshold are considered non-white
    non_white_mask = img_array < threshold 
    # Darken non-white pixels
    img_array[non_white_mask] = np.clip(img_array[non_white_mask] * darkening, 0, 255).astype(np.uint8)  
    # Convert back to PIL Image
    img_enhanced = Image.fromarray(img_array)  
    return img_enhanced 