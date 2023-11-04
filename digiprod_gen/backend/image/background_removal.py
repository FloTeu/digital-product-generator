
import requests
import replicate
from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil

def rembg(img_pil: Image) -> Image:
    model = "ilkerc/rembg:e809cddc666ccfd38a044f795cf65baab62eedc4273d096bf05935b9a3059b59"
    model = "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003"
    img_url = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil)}
    )
    return bytes2pil(requests.get(img_url, stream=True).content)


def easy_rem_bg(img_pil: Image) -> Image:
    model = "lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1"
    img_url = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil)}
    )
    return bytes2pil(requests.get(img_url, stream=True).content)


def extend_with_alpha(image):
    # If image already has an alpha channel, return it unchanged
    if image.mode.endswith("A"):
        return image

    # Create a new image with an alpha channel
    image_with_alpha = image.copy()
    image_with_alpha.putalpha(255)  # Set initial alpha value to fully opaque

    return image_with_alpha

def simple_remove_background(image_pil: Image, outer_pixel_range=30, tolerance=100):

    # Create a copy of the image to work with
    edited_image = extend_with_alpha(image_pil)

    # Get image dimensions
    width, height = image_pil.size

    # Calculate the average color of the 30 outer pixels
    outer_pixel_colors = []
    for x in range(outer_pixel_range):
        for y in range(height):
            outer_pixel_colors.append(image_pil.getpixel((x, y)))
        for y in range(height - outer_pixel_range, height):
            outer_pixel_colors.append(image_pil.getpixel((x, y)))
    for x in range(width - outer_pixel_range, width):
        for y in range(height):
            outer_pixel_colors.append(image_pil.getpixel((x, y)))
        for y in range(height - outer_pixel_range, height):
            outer_pixel_colors.append(image_pil.getpixel((x, y)))

    average_color = (
        sum([color[0] for color in outer_pixel_colors]) // len(outer_pixel_colors),
        sum([color[1] for color in outer_pixel_colors]) // len(outer_pixel_colors),
        sum([color[2] for color in outer_pixel_colors]) // len(outer_pixel_colors)
    )

    # Loop through the entire image and remove background
    edited_image_data = edited_image.load()  # Load pixel data for faster access
    for x in range(width):
        for y in range(height):
            pixel_color = edited_image_data[x, y]
            color_difference = sum([abs(pixel_color[i] - average_color[i]) for i in range(3)])
            if color_difference <= tolerance:
                edited_image_data[x, y] = (0, 0, 0, 0)  # Set to transparent pixel

    return edited_image




# def get_outer_greyscaled_pixel_range(img_np: np.ndarray, until_n_col=10) -> Tuple[int, int]:
#     """Returns grey scaled min and max value of outer (first until_n_col) pixels"""
#     return img_np[0:until_n_col].min(), img_np[0:until_n_col].max()


# def remove_outer_pixels(img_pil: Image, buffer: int=0) -> Image:
#     """Background removal of outer pixels
#
#     :param img_pil: Input image in pillow format
#     :param buffer: Additional puffer for the background removal threshold. Higher -> more pixels will be removed
#     :return:
#     """
#     import cv2
#     img_np = pil2cv(img_pil)
#
#     # Convert image to image gray
#     tmp = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
#
#     outer_min, outer_max = get_outer_greyscaled_pixel_range(tmp)
#     height, width = tmp.shape
#     print("outer_min, outer_max", outer_min, outer_max, tmp.shape, tmp[int(width*0.85), int(width*0.25)], img_np[int(width*0.85), int(width*0.25)])
#
#     # Applying thresholding technique
#     #_, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
#     alpha_mask = cv2.inRange(tmp, np.array([outer_min - buffer]), np.array([outer_max + buffer]))
#     # Invert the mask
#     alpha = 255 - alpha_mask
#
#     # Using cv2.split() to split channels
#     # of coloured image
#     b, g, r = cv2.split(img_np)
#
#     # Making list of Red, Green, Blue
#     # Channels and alpha
#     rgba = [b, g, r, alpha]
#
#     # Using cv2.merge() to merge rgba
#     # into a coloured/multi-channeled image
#     dst = cv2.merge(rgba, 4)
#
#     # transform back to pil
#     return cv2pil(dst)
