from fastapi import FastAPI
from routes import router
from handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)