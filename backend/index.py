"""
AI Medical Report Simplifier
Copyright (c) 2026 Sargam Chicholikar
Licensed under MIT License
"""

import os
import time
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel

# Internal Module Imports
from data_collector import data_collector
from analytics_tracker import analytics_tracker
from feedback_collector import feedback_collector
from excel_exporter import excel_exporter
from drug_database import DRUG_COMBINATIONS
from drug_service import drug_service
from ocr_module import PrescriptionOCR, LabReportParser
from ai_lab_analyzer import ai_lab_analyzer
from drug_translator import drug_translator
from advanced_xray_vision import advanced_xray_analyzer
from voice_generator import voice_generator

# Load environment variables
load_dotenv()

app = FastAPI(title="MediSimplify API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize engines
print("\n" + "="*60)
print("Initializing MediSimplify Systems...")
ocr_engine = PrescriptionOCR()
lab_parser = LabReportParser()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
print("✅ All systems ready!\n")

# Pydantic Models
class DrugQuery(BaseModel):
    drug_names: List[str]
    language: Optional[str] = "English"

class LabResult(BaseModel):
    test_name: str
    value: float

class LabQuery(BaseModel):
    results: List[LabResult]
    language: Optional[str] = "English"

def validate_drug_sync(drug_name):
    return drug_service.get_drug_info(drug_name)

# ==================== STATIC FILES & FRONTEND ====================

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>MediSimplify API is Running</h1><p>Frontend index.html not found.</p>")

@app.get("/styles.css")
async def serve_css():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "styles.css")
    return FileResponse(path) if os.path.exists(path) else HTTPException(404)

@app.get("/script.js")
async def serve_js():
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "script.js")
    return FileResponse(path) if os.path.exists(path) else HTTPException(404)

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    about_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "about.html")
    try:
        with open(about_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse("<h1>About page not found</h1>")

# ==================== CORE API LOGIC ====================

@app.post("/analyze-drugs")
def analyze_drugs(query: DrugQuery):
    language = query.language or "English"
    drugs_info = []
    validated_names = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(validate_drug_sync, d): d for d in query.drug_names}
        for future in futures:
            try:
                drug_info = future.result(timeout=40)
                if drug_info["confidence"] != "none":
                    drugs_info.append({
                        "name": drug_info["name"],
                        "treats": drug_info["treats"],
                        "explanation": drug_info.get("simple_explanation", "N/A"),
                        "dosage": drug_info.get("common_dosage", "N/A"),
                        "frequency": drug_info["frequency"],
                        "warnings": drug_info["warnings"]
                    })
                    validated_names.append(drug_info["name"].lower())
            except:
                pass
    
    if language != "English":
        drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    # Check for drug combinations/conditions
    detected_conditions = []
    drug_set = frozenset(validated_names)
    for combo, info in DRUG_COMBINATIONS.items():
        if combo.issubset(drug_set):
            detected_conditions.append({"condition": info["condition"], "explanation": info["explanation"]})

    analytics_tracker.track_prescription_analysis(language, False)
    return JSONResponse({"drugs": drugs_info, "detected_conditions": detected_conditions})

@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    contents = await file.read()
    result = ocr_engine.process_prescription(contents)
    data_collector.save_prescription(contents, result["found_drugs"], "English")
    analytics_tracker.track_prescription_analysis("English", True)
    return JSONResponse({"success": True, "found_drugs": result["found_drugs"]})

@app.post("/upload-lab-report")
async def upload_lab_report(file: UploadFile = File(...), language: str = Query("English")):
    contents = await file.read()
    is_pdf = file.content_type == "application/pdf"
    result = lab_parser.process_lab_report(contents, is_pdf)
    ai_analyses = ai_lab_analyzer.analyze_full_report_text(result["extracted_text"], language)
    data_collector.save_lab_report(contents, file.filename, ai_analyses, language)
    analytics_tracker.track_lab_analysis(language)
    return JSONResponse({"success": True, "ai_analysis": ai_analyses})

@app.post("/upload-xray")
async def upload_xray(file: UploadFile = File(...), language: str = Query("English")):
    contents = await file.read()
    xray_analysis = advanced_xray_analyzer.analyze_xray_detailed(contents, language)
    data_collector.save_xray(contents, xray_analysis, language)
    analytics_tracker.track_xray_analysis(language)
    return JSONResponse({"success": True, "xray_analysis": xray_analysis})

@app.post("/analyze-complete")
async def analyze_complete(prescription: UploadFile = File(None), lab_report: UploadFile = File(None), language: str = Query("English")):
    drugs_info = []
    lab_analysis = []
    if prescription:
        pres_contents = await prescription.read()
        pres_result = ocr_engine.process_prescription(pres_contents)
        # Reuse logic for drug validation
        for d in pres_result["found_drugs"]:
            info = drug_service.get_drug_info(d)
            if info["confidence"] != "none":
                drugs_info.append(info)
    if lab_report:
        lab_contents = await lab_report.read()
        lab_result = lab_parser.process_lab_report(lab_contents, lab_report.content_type == "application/pdf")
        lab_analysis = ai_lab_analyzer.analyze_full_report_text(lab_result["extracted_text"], language)
    
    return JSONResponse({"drugs": drugs_info, "lab_analysis": lab_analysis})

@app.post("/generate-audio")
async def generate_audio(text: str, language: str = "English"):
    audio_path = voice_generator.text_to_speech(text, language)
    if audio_path and os.path.exists(audio_path):
        analytics_tracker.track_voice_usage("audio", language)
        return FileResponse(audio_path, media_type="audio/mpeg")
    raise HTTPException(500, "Audio generation failed")

# ==================== ADMIN & ANALYTICS ====================

@app.get("/admin/dashboard")
async def admin_dashboard(password: str = Query(None)):
    if password != ADMIN_PASSWORD:
        return HTMLResponse("<h1>🔒 Admin Access Required</h1><form><input type='password' name='password'><button>Enter</button></form>")
    path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard.html")
    return FileResponse(path) if os.path.exists(path) else HTMLResponse("Dashboard missing")

@app.get("/analytics")
def get_analytics():
    return JSONResponse(analytics_tracker.get_statistics())

@app.post("/submit-feedback")
async def submit_feedback(rating: int, comments: str = "", language: str = "English"):
    feedback_collector.save_feedback({'rating': rating, 'comments': comments, 'language': language})
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
