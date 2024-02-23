import json
from typing import Tuple, Type
from pathlib import Path
from PIL import Image
from digiprod_gen.backend.models.export import MBAExportUploadData
from glob import glob

def read_exported_data(dir_path: Path) -> Tuple[MBAExportUploadData, list[Image.Image]]:
    with open(dir_path / "export.json", "r") as fp:
        upload_data = json.load(fp)
    image_file_paths = glob(f"{dir_path}/*png") + glob(f"{dir_path}/*jpg") + glob(f"{dir_path}/*jpeg")
    images = []
    for image_file_path in image_file_paths:
        images.append(Image.open(image_file_path))
    return MBAExportUploadData(**upload_data), images


