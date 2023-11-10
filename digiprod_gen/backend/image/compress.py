import logging

from PIL import Image
from digiprod_gen.backend.image.utils import is_jpeg, is_png
from digiprod_gen.backend.image.conversion import pil_png_to_pil_jpeg

def jpeg_compress(img_pil: Image, quality: int=90) -> Image:
    img_pil.save("image-file-compressed.jpeg",
                        "JPEG",
                        optimize = True,
                        quality = quality)
    img_compressed = Image.open("image-file-compressed.jpeg")
    return img_compressed

def png_compress(img_pil: Image, quality: int=90) -> Image:
    img_pil.save("image-file-compressed.PNG",
                        optimize = True,
                        quality = quality)
    img_compressed = Image.open("image-file-compressed.PNG")
    return img_compressed

def compress(img_pil: Image, quality: int=90) -> Image:
    """
    Compresses the image size
    PNG files cannot be compressed in the same way, as JPEG images can.
    Therefore, PNG files are converted to JPED
    """
    if is_png(img_pil):
        logging.warning("PNG file will be converted to JPEG in order to compress size")
        img_pil = pil_png_to_pil_jpeg(img_pil)

    print("Size in mb before compressing", get_approximate_size_in_mb(img_pil), "Format", img_pil.format)
    if is_jpeg(img_pil):
        img_compressed = jpeg_compress(img_pil, quality)
    else:
        raise NotImplementedError
    print("Size in mb before compressing", get_approximate_size_in_mb(img_pil))
    return img_compressed

def get_approximate_size_in_mb(image):
    """
    Get the size of a Pillow image in MB.

    :param image: Pillow Image object
    :return: Size of the image in MB
    """
    # Get image dimensions and color depth (bytes per pixel)
    width, height = image.size
    bytes_per_pixel = len(image.getbands())

    # Calculate the size in bytes and convert to MB
    size_in_bytes = width * height * bytes_per_pixel
    size_in_mb = size_in_bytes / (1024 * 1024)

    return size_in_mb