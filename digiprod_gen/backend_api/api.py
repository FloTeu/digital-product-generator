from typing import List
from fastapi import FastAPI
from digiprod_gen.backend_api.models.mba import MBAProduct, CrawlingMBARequest

app = FastAPI()

@app.post("/browser/crawl_mba_overview")
async def crawl_mba_overview(crawling_request: CrawlingMBARequest) -> List[MBAProduct]:
    return [MBAProduct(
        asin="str",
        title="dawawd",
        brand="wad",
        image_url="daw",
        product_url="dwawad",
    )]