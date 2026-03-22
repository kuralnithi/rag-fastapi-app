from fastapi import APIRouter, File, UploadFile
import os
import shutil
from app.models.schema import QueryRequest, QueryResponse
from app.services.rag_service import rag, add_document

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    print("payload---",payload)
    answer = rag(payload.question)
    return {"answer": answer}

@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    # Create temp directory if not exists
    os.makedirs("temp_uploads", exist_ok=True)
    file_path = f"temp_uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        add_document(file_path)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            
    return {"message": f"File {file.filename} uploaded and indexed successfully!"}
