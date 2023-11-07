import requests
import openai
import os
from PIL import Image
from digiprod_gen.backend.image.common import replicate_generate, OutputFormat, OpenAIImageQuality
from digiprod_gen.backend.models.common import ImageGenerationSDXLLoraUrl

from io import BytesIO

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
    model = "stability-ai/sdxl:8beff3369e81422112d93b89ca01426147de542cd4684c244b673b105188fe5f"
    return replicate_generate(model, {"prompt": prompt, "apply_watermark": False}, output_format=OutputFormat.GENERATOR)

def generate_with_stable_diffusion_xl_lora(prompt: str, lora_url: ImageGenerationSDXLLoraUrl) -> Image:
    model = "zylim0702/sdxl-lora-customize-model:5a2b1cff79a2cf60d2a498b424795a90e26b7a3992fbd13b340f73ff4942b81e"
    return replicate_generate(model, {"Lora_url": lora_url.value, "prompt": prompt, "num_outputs": 1, "num_inference_steps": 30, "apply_watermark": False}, output_format=OutputFormat.GENERATOR)

def generate_with_stable_diffusion_xl_barbie(prompt: str) -> Image:
    return generate_with_stable_diffusion_xl_lora(prompt + " in the style of TOK", lora_url=ImageGenerationSDXLLoraUrl.BARBIE)

def generate_with_stable_diffusion_xl_shirt(prompt: str) -> Image:
    return generate_with_stable_diffusion_xl_lora(prompt + " in the style of TOK", lora_url=ImageGenerationSDXLLoraUrl.SHIRT)

def generate_with_dalle3(prompt: str, quality: OpenAIImageQuality = OpenAIImageQuality.STANDARD) -> Image:
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality=quality,
        n=1,
    )

    image_url = response.data[0].url
    response = requests.get(image_url)

    return Image.open(BytesIO(response.content))
