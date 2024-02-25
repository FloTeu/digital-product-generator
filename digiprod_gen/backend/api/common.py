import io
import logging
import sys
from functools import lru_cache

from PIL import Image
from fastapi import UploadFile

from digiprod_gen.backend.browser.crawling.utils.common import get_random_headers
from digiprod_gen.backend.browser.selenium_fns import SeleniumBrowser
from digiprod_gen.backend.utils import initialise_config, delete_files_in_path, is_debug


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("BackendAPI")

CONFIG = initialise_config("config/app-config.yaml")


@lru_cache()
def init_selenium_browser(session_id, proxy=None, allow_javascript: bool=False, disable_images: bool=True) -> SeleniumBrowser:
    # New browser is started per session and per proxy
    # get random user agent, each time new browser is created
    headers = get_random_headers()
    logger.info(f"Init selenium browser with session_id {session_id} and user agent {headers['user-agent']}")
    data_dir_path = CONFIG.browser.selenium_data_dir_path
    delete_files_in_path(data_dir_path)
    browser = SeleniumBrowser()
    browser.setup(headless=not is_debug(),
                  data_dir_path=data_dir_path,
                  proxy=proxy,
                  headers=headers,
                  allow_javascript=allow_javascript,
                  disable_images=disable_images
                  )
    return browser


def get_cached_browser(session_id: str, proxy: str | None = None, allow_javascript: bool=False, disable_images: bool=False):
    # get param "+" is encoded to whitespace. Therefore, we need to decode it again (auto decode of %2B via fastapi does not work for unknown reasons)
    proxy_decoded = proxy.replace(' ', '+') if proxy else None
    return init_selenium_browser(session_id, proxy_decoded, allow_javascript=allow_javascript, disable_images=disable_images)


async def get_image(image_file: UploadFile) -> Image:
    contents = await image_file.read()

    # Convert to a BytesIO object
    image_stream = io.BytesIO(contents)

    # Open the image as a Pillow Image
    return Image.open(image_stream)
