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

def GetImagesfromPath(path,scale1=20,scale2=4,imageUpgrade=,par1,par2):
    resampling = Image.Resampling.LANCZOS
    image = Image.open(path)
    image_width, image_height = image.size

    width1 = image_width-500
    height1 = 160
    zone1 = (0,0,width1,height1)
    premiereImage = image.crop(zone1)
    premiereImage = premiereImage.resize((width1*scale1,height1*scale1),resample=resampling)
    #premiereImage = CutImage(premiereImage,180)

    height2 = image_height-height1
    width2 = image_width
    print(height2)
    zone2 = (0,height1,image_width,image_height)
    deuxiemeImage = image.crop(zone2)
    deuxiemeImage = deuxiemeImage.resize((width2*scale2,height2*scale2),resample=resampling)
    #Noircit les characters
    #deuxiemeImage = CutImage(deuxiemeImage,180)
    return [premiereImage,deuxiemeImage]

def CutImage(image,threshold):
    gray_img = image.convert("L")
    pixels = gray_img.load()
# Loop through all pixels and set them to either black or white based on the threshold
    width, height = gray_img.size
    for x in range(width):
        for y in range(height):
            # Get pixel value
            pixel_value = pixels[x, y]
        
            # Set to black if below threshold, white if above
            if pixel_value < threshold:
                pixels[x, y] = 0  # Black
            else:
                pass
                #pixels[x, y] = 255  # White
    return gray_img

def ShiftImage(image,threshold,value):
    gray_img = image.convert("L")
    pixels = gray_img.load()
# Loop through all pixels and set them to either black or white based on the threshold
    width, height = gray_img.size
    for x in range(width):
        for y in range(height):
            # Get pixel value
            pixel_value = pixels[x, y]
            if pixel_value<value:
                pixels[x,y]=0
            elif pixel_value < threshold:
                pixels[x, y] -= value  # Black
            else:
                pixels[x, y] = 255  # White
    return gray_img

def BoostImage(image,threshold,value):
    pass
