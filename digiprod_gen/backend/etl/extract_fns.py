import json
from typing import Tuple, Type
from pathlib import Path
from PIL import Image
from digiprod_gen.backend.models.export import MBAUploadData


def read_exported_data(dir_path: Path) -> Tuple[Image.Image, MBAUploadData]:
    design_path = dir_path / "design.jpeg"
    export_data_path = dir_path / "export.json"
    with open(export_data_path, "r") as fp:
        upload_data = json.load(fp)
        return Image.open(design_path), MBAUploadData(**upload_data)


