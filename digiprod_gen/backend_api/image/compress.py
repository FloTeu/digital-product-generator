from PIL import Image

def jpeg_compress(img_pil: Image, quality: int=90) -> Image:
    print("Compress image...")
    img_pil.save("image-file-compressed.jpeg",
                        "JPEG",
                        optimize = True,
                        quality = quality)
    img_compressed = Image.open("image-file-compressed.jpeg")
    return img_compressed

def png_compress(img_pil: Image, quality: int=90) -> Image:
    print("Compress image...")
    img_pil.save("image-file-compressed.PNG",
                        optimize = True,
                        quality = quality)
    img_compressed = Image.open("image-file-compressed.PNG")
    return img_compressed