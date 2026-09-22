from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from api.handlers import router

app = FastAPI(title="Газовый каталог — Лаба 2")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
