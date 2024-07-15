import uvicorn
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()

@app.get("/")
def read_root():
    return {"status_code": 200, "detail": "ok", "result": "working"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.uvicorn_host, port=settings.uvicorn_port, reload=True)