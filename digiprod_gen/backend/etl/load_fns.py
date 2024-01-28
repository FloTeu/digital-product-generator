import json
from PIL import Image
from datetime import datetime
from pathlib import Path
from digiprod_gen.backend.models.export import MBAExportUploadData


def get_export_dir(search_term: str) -> Path:
    dt = datetime.now()
    time = dt.strftime("%H_%M_%S")
    return Path(f"export/{dt.date()}/{search_term.replace(' ', '_')}/{time}/")

def export_upload_mba_product(
        img_pil: Image,
        export_data: MBAExportUploadData,
        output_dir: Path | None = None,
        ) -> Path:
    if output_dir is None:
        output_dir = get_export_dir(export_data.processing_data.search_term)
    # make dir if not exists
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(f"{output_dir}/export.json", "w") as fp:
        json.dump(export_data.model_dump(), fp)  # encode dict into JSON
    img_pil.save(f"{output_dir}/design.jpeg")
    return output_dir
