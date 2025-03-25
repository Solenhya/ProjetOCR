import io
import base64

def convertImageB64(image):
        # Convert the image to a BytesIO object
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)  # Go to the beginning of the BytesIO stream

    # Convert the BytesIO object to a Base64 string
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
    return img_base64
