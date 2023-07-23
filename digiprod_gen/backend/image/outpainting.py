from typing import Tuple
from PIL import Image

from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil
from digiprod_gen.backend.image.common import replicate_generate, OutputFormat


def outpainting_with_paella(img_pil: Image, prompt: str, output_relativ_size: Tuple[float, float] = (1.5, 1.5)) -> Image:
    model = "arielreplicate/paella_fast_outpainting:2afe25a164af57f0cc890165c7680a2a16a38037978481d56e13ed600eb29b73"
    return replicate_generate(model, {"input_image": pil2bytes_io(img_pil), "prompt": prompt, "output_relativ_size": f"{output_relativ_size[0]},{output_relativ_size[1]}"}, output_format=OutputFormat.GENERATOR)
