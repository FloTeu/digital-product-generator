from PIL import Image

def get_mba_design_crop(image_pil: Image) -> Image:
    width, height = image_pil.size
    # Setting the points for cropped image
    left = width / 5
    top = height / 5
    right = 4 * (width / 5)
    bottom = 4 * (height / 5)
    # Cropped image of above dimension
    # (It will not change original image)
    return image_pil.crop((left, top, right, bottom))