import os
import requests

from PIL import Image
from digiprod_gen.backend.image.conversion import pil2b64_str


def get_gpt4_vision_payload(img_pil: Image, text: str) -> dict:
    b64_str = pil2b64_str(img_pil)
    return {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": text
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{b64_str}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }

def get_gpt4_vision_response(img_pil: Image, prompt: str) -> str | None:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }
    payload = get_gpt4_vision_payload(img_pil, prompt)
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    try:
        output = response.json().get("choices")[0].get("message").get("content")
        return output
    except Exception:
        print(f"Could not extract gpt4 output from {response.json()}")
        return None