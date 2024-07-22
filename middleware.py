from fastapi.middleware.cors import CORSMiddleware
from app.main import app

origins = ["http://127.0.0.1:8000", "http://0.0.0.0:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Hello World"}
