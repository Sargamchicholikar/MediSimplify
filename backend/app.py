"""
AI Medical Report Simplifier
Copyright (c) 2026 Sargam Chicholikar
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import os

import sys
import os

# Avoid Windows console Unicode crashes (e.g., emoji logs) during startup.
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(__file__))
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
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="MediSimplify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("\n" + "="*60)
print("Initializing MediSimplify...")
print("="*60)
ocr_engine = PrescriptionOCR()
lab_parser = LabReportParser()
print("✅ All systems ready!\n")

# Admin password
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

class DrugQuery(BaseModel):
    drug_names: List[str]
    language: Optional[str] = "English"

def validate_drug_sync(drug_name):
    return drug_service.get_drug_info(drug_name)

def _is_pdf_upload(upload: UploadFile) -> bool:
    content_type = (upload.content_type or "").lower()
    filename = (upload.filename or "").lower()
    return content_type.startswith("application/pdf") or filename.endswith(".pdf")

def _is_image_upload(upload: UploadFile) -> bool:
    content_type = (upload.content_type or "").lower()
    filename = (upload.filename or "").lower()
    image_exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".tif")
    return content_type.startswith("image/") or filename.endswith(image_exts)

# ==================== STATIC FILES ====================

@app.get("/styles.css", response_class=FileResponse)
async def serve_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "styles.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(404)

@app.get("/script.js", response_class=FileResponse)
async def serve_js():
    js_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "script.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(404)

# ==================== FRONTEND ====================

@app.get("/", response_class=FileResponse)
async def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>MediSimplify</h1>")

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    """Serve about page"""
    about_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "about.html")
    try:
        with open(about_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        print(f"Error loading about.html: {e}")
        return HTMLResponse("<h1>About page not found</h1>")

# ==================== DRUG ANALYSIS ====================

@app.post("/analyze-drugs")
def analyze_drugs(query: DrugQuery):
    language = query.language or "English"
    drugs_info = []
    
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
            except:
                pass
    
    if language != "English":
        drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    analytics_tracker.track_prescription_analysis(language, False)
    
    return JSONResponse({"drugs": drugs_info, "detected_conditions": []})

# ==================== UPLOADS ====================

@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    if not _is_image_upload(file):
        raise HTTPException(400, "Images only")
    
    contents = await file.read()
    result = ocr_engine.process_prescription(contents)
    
    data_collector.save_prescription(contents, result["found_drugs"], "English")
    analytics_tracker.track_prescription_analysis("English", True)
    
    return JSONResponse({"success": True, "found_drugs": result["found_drugs"]})

@app.post("/upload-lab-report")
async def upload_lab_report(file: UploadFile = File(...), language: str = Query("English")):
    contents = await file.read()
    is_pdf = _is_pdf_upload(file)
    
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
async def analyze_complete(
    prescription: UploadFile = File(None),
    lab_report: UploadFile = File(None),
    language: str = Query("English")
):
    drugs_info = []
    lab_analysis = []
    
    if prescription:
        if not _is_image_upload(prescription):
            raise HTTPException(400, "Prescription must be an image file")
        pres_contents = await prescription.read()
        pres_result = ocr_engine.process_prescription(pres_contents)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(validate_drug_sync, d): d for d in pres_result["found_drugs"]}
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
                except:
                    pass
        
        if language != "English":
            drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    if lab_report:
        lab_contents = await lab_report.read()
        is_pdf = _is_pdf_upload(lab_report)
        lab_result = lab_parser.process_lab_report(lab_contents, is_pdf)
        lab_analysis = ai_lab_analyzer.analyze_full_report_text(lab_result["extracted_text"], language)
    
    return JSONResponse({"drugs": drugs_info, "detected_conditions": [], "lab_analysis": lab_analysis})

# ==================== VOICE ====================

@app.post("/generate-audio")
async def generate_audio(text: str, language: str = "English"):
    audio_path = voice_generator.text_to_speech(text, language)
    if audio_path and os.path.exists(audio_path):
        analytics_tracker.track_voice_usage("audio", language)
        return FileResponse(audio_path, media_type="audio/mpeg")
    raise HTTPException(500, "Audio failed")

# ==================== FEEDBACK ====================

@app.post("/submit-feedback")
async def submit_feedback(
    rating: int = Query(..., ge=1, le=5),
    comments: str = Query(""),
    feature_used: str = Query("general"),
    language: str = Query("English"),
    email: str = Query("anonymous"),
    feedback_type: str = Query("general")
):
    feedback_id = feedback_collector.save_feedback({
        'rating': rating, 'comments': comments, 'feature_used': feature_used,
        'language': language, 'email': email, 'feedback_type': feedback_type
    })
    return JSONResponse({'success': True, 'feedback_id': feedback_id})

@app.get("/feedback-stats")
def get_feedback_stats():
    return JSONResponse(feedback_collector.get_statistics())

# ==================== ADMIN ROUTES ====================

@app.get("/admin/dashboard")
async def admin_dashboard(password: str = Query(None)):
    if password != ADMIN_PASSWORD:
        return HTMLResponse("""
            <html><body style="font-family: Arial; text-align: center; padding: 100px; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0;">
                <div style="background: white; padding: 40px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                    <h1>🔒 Admin Access</h1>
                    <form method="get">
                        <input type="password" name="password" placeholder="Password" required autofocus
                               style="padding: 12px 20px; font-size: 1rem; border: 2px solid #4f46e5; border-radius: 8px; margin: 10px;">
                        <button type="submit" style="padding: 12px 24px; background: #4f46e5; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
                            Access Dashboard
                        </button>
                    </form>
                </div>
            </body></html>
        """)
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return HTMLResponse("<h1>Dashboard not found</h1>")

@app.get("/admin/analytics-data")
async def admin_analytics_data(password: str = Query(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    return JSONResponse(analytics_tracker.get_statistics())

@app.get("/admin/feedback-data")
async def admin_feedback_data(password: str = Query(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    return JSONResponse({
        'stats': feedback_collector.get_statistics(),
        'all_feedback': feedback_collector.get_all_feedback()
    })

@app.get("/admin/dataset-data")
async def admin_dataset_data(password: str = Query(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    return JSONResponse(data_collector.get_statistics())

@app.get("/admin/export-excel")
async def admin_export_excel(password: str = Query(...)):
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    
    filepath = excel_exporter.export_combined()
    if filepath and os.path.exists(filepath):
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    raise HTTPException(500, "Export failed")

# ==================== ANALYTICS ====================

@app.get("/analytics")
def get_analytics():
    return JSONResponse(analytics_tracker.get_statistics())

@app.get("/dataset-stats")
def dataset_stats():
    return JSONResponse(data_collector.get_statistics())

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print(" "*20 + "🏥 MediSimplify")
    print("="*70)
    print("\n📍 App:       http://127.0.0.1:8000/")
    print("🔒 Dashboard: http://127.0.0.1:8000/admin/dashboard")
    print("="*70 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
