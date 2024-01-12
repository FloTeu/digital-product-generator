from PIL import Image
from digiprod_gen.backend.models.export import MBAExportUploadData
from digiprod_gen.backend.models.session import SessionState

def import_selected_product(img_pil: Image, upload_data: MBAExportUploadData, session_state: SessionState):

    # Status update
    session_state.status.refresh()
    session_state.status.listing_generated = True
    session_state.status.prompts_generated = True
    session_state.status.keywords_extracted = True
    session_state.status.product_imported = True

    # Upload data update
    session_state.upload_data.brand = upload_data.product_data.brand
    session_state.upload_data.title = upload_data.product_data.title
    session_state.upload_data.bullet_1 = upload_data.product_data.bullets[0]
    session_state.upload_data.bullet_2 = upload_data.product_data.bullets[1]
    session_state.upload_data.description = upload_data.product_data.description
    session_state.upload_data.predicted_brands = upload_data.processing_data.brand_suggestions
    session_state.upload_data.predicted_titles = upload_data.processing_data.title_suggestions
    session_state.upload_data.predicted_bullets = upload_data.processing_data.bullet_suggestions
    session_state.upload_data.settings = upload_data.mba_upload_settings

    # image data update
    session_state.image_gen_data.image_gen_prompts = upload_data.processing_data.prompt_suggestions
    session_state.image_gen_data.image_gen_prompt_selected = upload_data.processing_data.prompt
    session_state.image_gen_data.image_pil_generated = img_pil
    session_state.image_gen_data.image_pil_upscaled = None
    session_state.image_gen_data.image_pil_background_removed = None
    session_state.image_gen_data.image_pil_upload_ready = None
    session_state.image_gen_data.image_pil_outpainted = None
