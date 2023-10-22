from enum import Enum

import replicate
import requests
from PIL import Image

from digiprod_gen.backend_api.image.conversion import bytes2pil


class OutputFormat(Enum):
    STRING="str"
    GENERATOR="generator"


def replicate_generate(model_version: str, input: dict, output_format: OutputFormat = OutputFormat.STRING) -> Image:
    output = replicate.run(
        model_version,
        input=input
    )
    if output_format == OutputFormat.STRING:
        img_url = output
    if output_format == OutputFormat.GENERATOR:
        for output_i in output:
            img_url = output_i
    return bytes2pil(requests.get(img_url, stream=True).content)
