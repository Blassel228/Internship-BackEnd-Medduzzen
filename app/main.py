import uvicorn
from fastapi import FastAPI
from config import settings

app = FastAPI()

@app.get("/")
def read_root():
    return {"status_code": 200, "detail": "ok", "result": "working"}

@app.get("/health_check")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)