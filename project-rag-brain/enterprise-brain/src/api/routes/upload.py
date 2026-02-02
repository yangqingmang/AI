from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
import shutil
import os
import glob
from typing import List
from src.config.settings import get_settings
from src.core.ingest import ingest_docs
from src.api.schemas import UploadResponse

router = APIRouter()
settings = get_settings()

@router.get("/files", response_model=List[str])
def list_files():
    """List all files in the knowledge base directory."""
    try:
        if not os.path.exists(settings.DATA_DIR):
            return []
        # Get all files
        files = []
        for ext in ["*.pdf", "*.txt", "*.md"]:
            # glob matches are full paths
            found = glob.glob(os.path.join(settings.DATA_DIR, ext))
            files.extend([os.path.basename(f) for f in found])
        return sorted(files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=UploadResponse)
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # Ensure data directory exists
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        
        # Save file to data directory
        file_location = os.path.join(settings.DATA_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger ingestion in background
        background_tasks.add_task(ingest_docs)
        
        return UploadResponse(filename=file.filename, status="File uploaded and ingestion triggered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
