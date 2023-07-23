from PIL import Image
from digiprod_gen.backend.image.common import replicate_generate, OutputFormat


def generate_with_deepfloyd_if(prompt: str) -> Image:
    model = "andreasjansson/deepfloyd-if:fb84d659df149f4515c351e394d22222a94144aa1403870c36025c8b28846c8d"
    return replicate_generate(model, {"prompt": prompt}, output_format=OutputFormat.STRING)

def generate_with_openjourney(prompt: str) -> Image:
    model = "prompthero/openjourney:ad59ca21177f9e217b9075e7300cf6e14f7e5b4505b87b9689dbd866e9768969"
    prompt = f"mdjrny-v4 style {prompt}"
    return replicate_generate(model, {"prompt": prompt}, output_format=OutputFormat.GENERATOR)

def generate_with_pokemon(prompt: str) -> Image:
    model = "lambdal/text-to-pokemon:ff6cc781634191dd3c49097a615d2fc01b0a8aae31c448e55039a04dcbf36bba"
    return replicate_generate(model, {"prompt": prompt}, output_format=OutputFormat.GENERATOR)

def generate_with_waifu(prompt: str) -> Image:
    model = "cjwbw/waifu-diffusion:25d2f75ecda0c0bed34c806b7b70319a53a1bccad3ade1a7496524f013f48983"
    return replicate_generate(model, {"prompt": prompt}, output_format=OutputFormat.GENERATOR)

def generate_with_stable_diffusion(prompt: str) -> Image:
    model = "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4"
    return replicate_generate(model, {"prompt": prompt}, output_format=OutputFormat.GENERATOR)

