
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import datetime

from .database import engine, get_db
from .models import Base, RFP, ComplianceFinding, Estimate, EstimateLine
from .schemas import (
    RFPUpload, RFPResponse, ComplianceFindingResponse, 
    EstimateResponse, EstimateCreate
)
from .services.rfp_service import process_rfp_upload, extract_text_from_file
from .services.lint_service import lint_rfp
from .services.estimate_service import create_estimate_from_findings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BuildForge Cloud API",
    description="A production-grade, BIM-aware, ERP-connected AEC SaaS API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:41826"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for generated reports
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

@app.get("/")
async def root():
    return {"message": "BuildForge Cloud API", "version": "0.1.0"}

@app.post("/rfp/upload", response_model=RFPResponse)
async def upload_rfp(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload an RFP document (PDF, DOCX, or text)"""
    try:
        rfp = await process_rfp_upload(db, file, project_id)
        return rfp
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process RFP: {str(e)}")

@app.post("/rfp/{rfp_id}/lint", response_model=List[ComplianceFindingResponse])
async def lint_rfp_endpoint(
    rfp_id: str,
    ruleset_version: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Lint an RFP against compliance rules"""
    try:
        findings = await lint_rfp(db, rfp_id, ruleset_version)
        return findings
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to lint RFP: {str(e)}")

@app.get("/rfp/{rfp_id}/report")
async def get_rfp_report(
    rfp_id: str,
    format: str = "json",  # json, html, pdf
    db: Session = Depends(get_db)
):
    """Get RFP compliance report in various formats"""
    # TODO: Implement report generation
    raise HTTPException(status_code=501, detail="Report generation not implemented yet")

@app.post("/estimate/from_lint", response_model=EstimateResponse)
async def create_estimate_from_lint(
    estimate_data: EstimateCreate,
    db: Session = Depends(get_db)
):
    """Create estimate from compliance findings"""
    try:
        estimate = await create_estimate_from_findings(db, estimate_data)
        return estimate
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create estimate: {str(e)}")

@app.get("/estimate/{estimate_id}/export")
async def export_estimate(
    estimate_id: str,
    format: str = "csv",  # csv, pdf
    db: Session = Depends(get_db)
):
    """Export estimate in various formats"""
    # TODO: Implement estimate export
    raise HTTPException(status_code=501, detail="Estimate export not implemented yet")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
