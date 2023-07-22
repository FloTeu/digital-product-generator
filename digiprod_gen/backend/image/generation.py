import requests
import replicate

from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io, bytes2pil
from enum import Enum

class OutputFormat(Enum):
    STRING="str"
    GENERATOR="generator"

def generate(prompt: str, replicate_model_url: str, output_format: OutputFormat = OutputFormat.STRING) -> Image:
    output = replicate.run(
        replicate_model_url,
        input={"prompt": prompt}
    )
    if output_format == OutputFormat.STRING:
        img_url = output
    if output_format == OutputFormat.GENERATOR:
        for output_i in output:
            img_url = output_i
    return bytes2pil(requests.get(img_url, stream=True).content)

def generate_with_deepfloyd_if(prompt: str) -> Image:
    model = "andreasjansson/deepfloyd-if:fb84d659df149f4515c351e394d22222a94144aa1403870c36025c8b28846c8d"
    return generate(prompt, model, output_format=OutputFormat.STRING)

def generate_with_openjourney(prompt: str) -> Image:
    model = "prompthero/openjourney:ad59ca21177f9e217b9075e7300cf6e14f7e5b4505b87b9689dbd866e9768969"
    prompt = f"mdjrny-v4 style {prompt}"
    return generate(prompt, model, output_format=OutputFormat.GENERATOR)

def generate_with_pokemon(prompt: str) -> Image:
    model = "lambdal/text-to-pokemon:ff6cc781634191dd3c49097a615d2fc01b0a8aae31c448e55039a04dcbf36bba"
    return generate(prompt, model, output_format=OutputFormat.GENERATOR)
