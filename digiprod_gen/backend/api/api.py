import uvicorn
from fastapi import FastAPI
from digiprod_gen.backend.api.endpoints import browser, status, image

app = FastAPI()
app.include_router(browser.router, prefix="/browser", tags=["browser"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(image.router, prefix="/image", tags=["image"])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)