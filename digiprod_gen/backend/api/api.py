import uvicorn
from fastapi import FastAPI
from digiprod_gen.backend.api.endpoints import browser, status

app = FastAPI()
app.include_router(browser.router, prefix="/browser", tags=["browser"])
app.include_router(status.router, prefix="/status", tags=["status"])



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)