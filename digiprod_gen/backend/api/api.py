import uvicorn
from fastapi import FastAPI
from digiprod_gen.backend.api.endpoints import browser, status, image, text, research

app = FastAPI()
app.include_router(research.router, prefix="/research", tags=["research"])
app.include_router(browser.router, prefix="/browser", tags=["browser"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(image.router, prefix="/image", tags=["image"])
app.include_router(text.router, prefix="/text", tags=["text"])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)