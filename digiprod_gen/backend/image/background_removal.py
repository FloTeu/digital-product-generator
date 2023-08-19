
import requests
import numpy as np
import replicate
from PIL import Image
from typing import Tuple
from digiprod_gen.backend.image.conversion import pil2cv, cv2pil, pil2bytes_io, bytes2pil

def rembg(img_pil: Image) -> Image:
    model = "ilkerc/rembg:e809cddc666ccfd38a044f795cf65baab62eedc4273d096bf05935b9a3059b59"
    model = "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003"
    img_url = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil)}
    )
    return bytes2pil(requests.get(img_url, stream=True).content)


def get_outer_greyscaled_pixel_range(img_np: np.ndarray, until_n_col=10) -> Tuple[int, int]:
    """Returns grey scaled min and max value of outer (first 30) pixels"""
    return img_np[0:until_n_col].min(), img_np[0:until_n_col].max()

def remove_outer_pixels(img_pil: Image, buffer: int=0) -> Image:
    """Background removal of outer pixels

    :param img_pil: Input image in pillow format
    :param buffer: Additional puffer for the background removal threshold. Higher -> more pixels will be removed
    :return:
    """
    import cv2
    img_np = pil2cv(img_pil)

    # Convert image to image gray
    tmp = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    outer_min, outer_max = get_outer_greyscaled_pixel_range(tmp)

    # Applying thresholding technique
    #_, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    alpha_mask = cv2.inRange(tmp, np.array([outer_min - buffer]), np.array([outer_max + buffer]))
    # Invert the mask
    alpha = 255 - alpha_mask

    # Using cv2.split() to split channels
    # of coloured image
    b, g, r = cv2.split(img_np)

    # Making list of Red, Green, Blue
    # Channels and alpha
    rgba = [b, g, r, alpha]

    # Using cv2.merge() to merge rgba
    # into a coloured/multi-channeled image
    dst = cv2.merge(rgba, 4)

    # transform back to pil
    return cv2pil(dst)

