import json
from PIL import Image
from datetime import datetime
from pathlib import Path
from digiprod_gen.backend.models.export import MBAExportUploadData


def export_upload_mba_product(
        img_pil: Image,
        export_data: MBAExportUploadData,
        output_dir: Path | None = None,
        ):
    if output_dir is None:
        dt = datetime.now()
        time = dt.strftime("%H_%M_%S")
        output_dir = Path(f"export/{dt.date()}/{export_data.processing_data.search_term.replace(' ','_')}/{time}/")
    # make dir if not exists
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(f"{output_dir}/export.json", "w") as fp:
        json.dump(export_data.model_dump(), fp)  # encode dict into JSON
    img_pil.save(f"{output_dir}/design.jpeg")
