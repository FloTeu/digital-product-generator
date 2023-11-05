from PIL import Image
from digiprod_gen.frontend.backend_caller import BackendCaller
from digiprod_gen.backend.utils import initialise_config
from digiprod_gen.backend.models.config import DigiProdGenConfig
from digiprod_gen.backend.models.request import UploadMBARequest, MBAUploadSettings
from digiprod_gen.backend.image import conversion


CONFIG: DigiProdGenConfig = initialise_config(
    config_file_path="config/app-config.yaml"
)

def test_mba_product_upload():
    """Test if backend api for product upload works as intended"""
    backend_caller = BackendCaller(CONFIG.backend)
    session_id="23123"
    settings = MBAUploadSettings(product_categories=["Shirt"], marketplaces=["de","com"], colors=["Black"], fit_types=["Men"])
    upload_request = UploadMBARequest(
        title="Test title",
        brand="Test brand",
        bullet_1="Test bullet 1",
        settings=settings.model_dump()
    )
    request_data = {**settings.model_dump(), "title": upload_request.title, "brand": upload_request.brand, "bullet_1": upload_request.bullet_1, "bullet_2": upload_request.bullet_2, "description": upload_request.description}
    image_pil_upload_ready = Image.open("/Users/fteutsch/Downloads/export (72).png")
    image_byte_array = conversion.pil2bytes_io(image_pil_upload_ready, format="PNG")
    image_byte_array.seek(0)
    files = {
        "image_upload_ready": ("image_upload_ready.png", image_byte_array, 'image/png')
    }

    headers = {
        'accept': 'application/json',
    }

    response = backend_caller.post(
        f"/browser/upload/upload_mba_product?session_id={session_id}",
        headers=headers, data=request_data, files=files
    )
    assert response.status_code == 200

