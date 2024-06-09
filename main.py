from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from handlers import register_exception_handlers
import os

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
from routes import router

register_exception_handlers(app)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    
