import json
from typing import Tuple, Type
from pathlib import Path
from PIL import Image
from digiprod_gen.backend.models.export import MBAExportUploadData


def read_exported_data(dir_path: Path) -> Tuple[Image.Image, MBAExportUploadData]:
    design_path = dir_path / "design.jpeg"
    # if jpeg does not exist try png
    if not design_path.is_file():
        design_path = dir_path / "design.png"
    export_data_path = dir_path / "export.json"
    with open(export_data_path, "r") as fp:
        upload_data = json.load(fp)
        return Image.open(design_path), MBAExportUploadData(**upload_data)


