import base64
import io
from io import BytesIO
from PIL import Image
import numpy as np

def bytes2bytes_io(image_bytes: bytes) -> BytesIO:
    return BytesIO(image_bytes)

def bytes2pil(image_bytes: bytes) -> Image:
    return bytes_io2pil(bytes2bytes_io(image_bytes))

def bytes_io2pil(img_bytes_io: BytesIO):
    img_bytes_io.seek(0)  # Ensure you're at the start of the BytesIO object
    return Image.open(img_bytes_io)

def pil2bytes_io(img_pil: Image, format="PNG") -> BytesIO:
    img_byte_arr = BytesIO()
    img_pil.save(img_byte_arr, format=format)
    return img_byte_arr

def pil2bytes(img_pil: Image) -> bytes:
    return pil2bytes_io(img_pil).getvalue()

def pil2np(img_pil: Image):
    return np.array(img_pil)

def cv2pil(img_cv):
    import cv2
    code = cv2.COLOR_BGR2RGBA if img_cv.shape[2] == 4 else cv2.COLOR_BGR2RGB
    # You may need to convert the color.
    img = cv2.cvtColor(img_cv, code)
    return Image.fromarray(img)

def pil2cv(img_pil):
    # https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
    img_np = pil2np(img_pil.convert('RGB'))
    # Convert RGB to BGR
    return img_np[:, :, ::-1].copy()

def np2pil(img_np):
    return Image.fromarray(img_np)


def pil2b64_str(img):
    img_bytes = pil2bytes(img)
    base64_bytes = base64.b64encode(img_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def pil2b64_str(img):
    img_bytes = pil2bytes(img)
    base64_bytes = base64.b64encode(img_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def b64_str2bytes(b64_str):
    # str to base64 bytes
    b64_bytes = b64_str.encode('utf-8')
    # base64bytes to normal bytes
    img_bytes = base64.b64decode(b64_bytes)
    return img_bytes


def b64_str2pil(b64_str) -> Image:
    return bytes2pil(b64_str2bytes(b64_str))

def pilrgba2pilrgb(img_pil: Image) -> Image:
    # Convert the 4-channel image to a 3-channel image (RGB)
    if img_pil.mode == "RGBA":
        return img_pil.convert("RGB")
    elif img_pil.mode == "RGB":
        return img_pil
    else:
        raise NotImplementedError(f"Mode is not yet implemented for rgb conversion {img_pil.mode}")

def pil_png2pil_jpeg(img_pil: Image) -> Image:
    """
    Convert a PNG image (Pillow Image object) to a format suitable for JPEG and set format to 'JPEG'.

    :param img_pil: Pillow Image object (assumed to be PNG).
    :return: Pillow Image object with format set to 'JPEG'.
    """
    if img_pil.mode in ('RGBA', 'LA') or (
            img_pil.mode == 'P' and 'transparency' in img_pil.info):
        # Create a white background
        background = Image.new('RGB', img_pil.size, (255, 255, 255))
        # Paste the image on the background, using transparency mask
        background.paste(img_pil, mask=img_pil.split()[-1])
        img_pil = background
    else:
        # Convert to RGB if not already in that mode
        img_pil = img_pil.convert('RGB')

    # Save to a BytesIO object and reload to set format to 'JPEG'
    byte_io = io.BytesIO()
    img_pil.save(byte_io, 'JPEG')
    byte_io.seek(0)
    return Image.open(byte_io)

def pil2pil_png(img_pil: Image) -> Image:
    # Save the image in a new BytesIO object as PNG
    png_bytesio = io.BytesIO()
    img_pil.save(png_bytesio, format='PNG')
    png_bytesio.seek(0)

    # Reload the image from the new BytesIO object
    return Image.open(png_bytesio)

def ensure_rgba(img_pil: Image) -> Image:
    """
    Ensure the given image is in RGBA format

    :param img_pil: Pillow Image object.
    :return: Image in RGBA format.
    """
    if img_pil.mode != 'RGBA':
        # Convert to 'RGBA'
        img_pil = img_pil.convert('RGBA')

    return img_pil