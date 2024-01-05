import os
import replicate
import requests

from PIL import Image
from digiprod_gen.backend.image.conversion import pil2bytes_io
from digiprod_gen.backend.image.lvm_fns import get_gpt4_vision_response
from digiprod_gen.backend.utils import booleanize


def image2prompt(img_pil: Image) -> str:
    model = "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5"
    prompt = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil)}
    )
    return prompt


def image2prompt_gpt4(img_pil: Image) -> str | None:
    prompt = "Write only a text-to-image prompt which is able to generate a similar image"
    return get_gpt4_vision_response(img_pil, prompt)

def has_text_inprint(img_pil: Image) -> bool:
    model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
    answer = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil),
               "question": "Does this t-shirt design include a text imprint with several words?"}
    )
    return booleanize(answer)

# def image2text_caption(img_pil: Image) -> str:
#     model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
#     text_caption = replicate.run(
#         model,
#         input={"image": pil2bytes_io(img_pil),
#                "question": "Write only the text imprint used on this picture"}
#     )
#     return text_caption

def image2text_caption(img_pil: Image) -> str | None:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    payload = get_gpt4_vision_payload(img_pil, "Return only the text caption. If no text caption exists, return nothing.")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    try:
        output = response.json().get("choices")[0].get("message").get("content")
        return output
    except Exception:
        print(f"Could not extract gpt4 output from {response.json()}")
        return None


def image2visual_caption(img_pil: Image) -> str:
    model = "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608"
    visual_caption = replicate.run(
        model,
        input={"image": pil2bytes_io(img_pil),
               "question": "Comprehensively describe the visual elements of this image, in order to recreate it"}
    )
    return visual_caption

