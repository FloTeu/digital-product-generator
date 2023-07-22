from io import BytesIO
from PIL import Image
import numpy as np

def bytes2bytes_io(image_bytes: bytes) -> BytesIO:
    return BytesIO(image_bytes)

def bytes2pil(image_bytes: bytes) -> Image:
    return Image.open(bytes2bytes_io(image_bytes))

def pil2bytes_io(img_pil: Image) -> BytesIO:
    img_byte_arr = BytesIO()
    img_pil.save(img_byte_arr, format='PNG')
    return img_byte_arr

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
