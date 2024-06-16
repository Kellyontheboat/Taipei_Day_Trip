from fastapi import FastAPI
from .routes import router
from .handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(router)

