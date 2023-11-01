import replicate
from digiprod_gen.backend.utils import init_environment
from PIL import Image
import requests
from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil


init_environment()

image_path = "/Users/fteutsch/Documents/Bilder/shirt-designs/digiprodgen/floteu_An_Otaku-style_kawaii_sloth_rocking_out_in_the_sky_with__a777f520-9d30-4d93-8563-e10c80aa7d19.png"
model = "daanelson/some-upscalers:3078c9717f1b83d4fa86890b769f047695daff189028b96dcf517747853a48b0"
model = "ilkerc/rembg:e809cddc666ccfd38a044f795cf65baab62eedc4273d096bf05935b9a3059b59"

img_buffer = open(image_path, "rb")
img_pil = Image.open(image_path)

output = replicate.run(
    model,
    input={"image": pil2bytes_io(img_pil)}
)

img_out = bytes2pil(requests.get(output, stream=True).content)

print(output)