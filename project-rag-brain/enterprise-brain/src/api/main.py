from fastapi import FastAPI
from src.api.routes import chat, upload, stream

app = FastAPI(title="Enterprise Brain API", version="1.0.0")

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(stream.router, prefix="/api/v1", tags=["Chat"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
