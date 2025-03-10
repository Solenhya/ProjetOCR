from PIL import Image

def ImagefromPath(path):
    image = Image.open("PilPlay.png")
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