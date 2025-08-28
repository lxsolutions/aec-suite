


import os
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import aiofiles
import magic
import pdfplumber
from docx import Document
from typing import Optional
import hashlib

from ..models import RFP

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_rfp_upload(db: Session, file: UploadFile, project_id: Optional[str] = None) -> RFP:
    """Process RFP file upload and extract text"""
    
    # Validate file type
    file_content = await file.read()
    mime_type = magic.from_buffer(file_content, mime=True)
    
    if mime_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or text files.")
    
    # Generate unique filename
    file_id = uuid.uuid4()
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    await file.seek(0)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(await file.read())
    
    # Extract text
    extracted_text = await extract_text_from_file(file_path, mime_type)
    text_hash = hashlib.sha256(extracted_text.encode()).hexdigest() if extracted_text else None
    
    # Create RFP record
    rfp = RFP(
        id=file_id,
        project_id=project_id,
        filename=filename,
        original_filename=file.filename,
        file_size=len(file_content),
        mime_type=mime_type,
        extracted_text=extracted_text,
        text_hash=text_hash,
        status="processed"
    )
    
    db.add(rfp)
    db.commit()
    db.refresh(rfp)
    
    return rfp

async def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """Extract text from various file types"""
    try:
        if mime_type == 'application/pdf':
            return await extract_text_from_pdf(file_path)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return await extract_text_from_docx(file_path)
        elif mime_type == 'text/plain':
            return await extract_text_from_txt(file_path)
        else:
            return ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")
    return text.strip()

async def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX extraction failed: {str(e)}")

async def extract_text_from_txt(file_path: str) -> str:
    """Extract text from text file"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text file reading failed: {str(e)}")

def get_rfp_by_id(db: Session, rfp_id: str) -> RFP:
    """Get RFP by ID"""
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return rfp


