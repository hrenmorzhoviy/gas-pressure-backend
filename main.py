from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from api.handlers import router
from api.gases import router as gases_api_router
from api.users import router as users_api_router

app = FastAPI(title="Газовый каталог — REST API", version="3.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
app.include_router(gases_api_router)
app.include_router(users_api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
