import io

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from digiprod_gen.backend.api.common import init_selenium_browser
from digiprod_gen.backend.browser.selenium_fns import get_full_page_screenshot

router = APIRouter()

@router.get("/browser_screenshot")
async def get_browser_screenshot(session_id: str, proxy: str | None = None) -> StreamingResponse:
    browser = init_selenium_browser(session_id, proxy)
    screenshot_bytes = get_full_page_screenshot(browser.driver)
    return StreamingResponse(io.BytesIO(screenshot_bytes), media_type="image/png")


@router.get("/browser_settings")
async def get_browser_settings(session_id: str, proxy: str | None = None) -> str:
    browser = init_selenium_browser(session_id, proxy)
    # Get the actual User-Agent used by the WebDriver
    user_agent = browser.driver.execute_script("return navigator.userAgent")

    # Access headers of a specific request (for example, the first request)
    request = browser.driver.requests[0]
    request_headers = request.headers
    response_headers = request.response.headers

    return f"""
    User Agent: {user_agent}\n\nProxy Config: {browser.driver.proxy}\n\nRequest Headers: {request_headers}\n\nResponse Headers: {response_headers}
    """
