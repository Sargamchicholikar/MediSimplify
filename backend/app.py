"""
AI Medical Report Simplifier
Copyright (c) 2026 Sargam Chicholikar
Licensed under MIT License

Original Author: Sargam Chicholikar
Email: work.sargam@gmail.com
GitHub: https://github.com/Sargamchicholikar
LinkedIn: https://linkedin.com/in/sargam-chicholikar
Created: February 2026
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import time
import os

from data_collector import data_collector
from analytics_tracker import analytics_tracker
from feedback_collector import feedback_collector
from drug_database import DRUG_COMBINATIONS, ABBREVIATIONS
from drug_service import drug_service
from lab_database import LAB_TESTS
from ocr_module import PrescriptionOCR, LabReportParser
from ai_lab_analyzer import ai_lab_analyzer
from drug_translator import drug_translator
from advanced_xray_vision import advanced_xray_analyzer
from voice_generator import voice_generator
from excel_exporter import excel_exporter

app = FastAPI(title="MediSimplify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

print("\n" + "="*60)
print("Initializing MediSimplify...")
print("="*60)
ocr_engine = PrescriptionOCR()
lab_parser = LabReportParser()
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


# ==================== FRONTEND ====================

@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve main page"""
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
    except:
        return HTMLResponse("<h1>About (Local only)</h1>")


# ==================== DRUG ANALYSIS ====================

@app.post("/analyze-drugs")
def analyze_drugs(query: DrugQuery):
    """Manual drug entry with tracking"""
    language = query.language or "English"
    
    print(f"\n🚀 {len(query.drug_names)} drugs in {language}")
    
    drugs_info = []
    validated_drugs = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(validate_drug_sync, d): d for d in query.drug_names}
        
        for future in futures:
            drug_name = futures[future]
            try:
                drug_info = future.result(timeout=40)
                
                drugs_info.append({
                    "name": drug_info["name"],
                    "treats": drug_info["treats"],
                    "explanation": drug_info.get("simple_explanation", "N/A"),
                    "dosage": drug_info.get("common_dosage", "N/A"),
                    "frequency": drug_info["frequency"],
                    "warnings": drug_info["warnings"]
                })
                
                if drug_info["confidence"] != "none":
                    validated_drugs.append(drug_name.lower().strip())
                    print(f"✅ {drug_name}")
            except Exception as e:
                print(f"❌ {drug_name}: {e}")
    
    if language != "English":
        drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    detected_conditions = []
    drug_set = frozenset(validated_drugs)
    
    for combo, info in DRUG_COMBINATIONS.items():
        if combo.issubset(drug_set):
            detected_conditions.append({
                "condition": info["condition"],
                "explanation": info["explanation"]
            })
    
    # Track
    analytics_tracker.track_prescription_analysis(language, False)
    
    return JSONResponse(content={
        "drugs": drugs_info,
        "detected_conditions": detected_conditions
    })


# ==================== PRESCRIPTION ====================

@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    """Prescription upload with tracking"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Images only")
    
    try:
        contents = await file.read()
        result = ocr_engine.process_prescription(contents)
        
        data_collector.save_prescription(contents, result["found_drugs"], "English")
        analytics_tracker.track_prescription_analysis("English", True)
        
        return JSONResponse({
            "success": True,
            "found_drugs": result["found_drugs"],
            "drug_count": len(result["found_drugs"])
        })
    except Exception as e:
        raise HTTPException(500, str(e))


# ==================== LAB REPORT ====================

@app.post("/upload-lab-report")
async def upload_lab_report(file: UploadFile = File(...), language: str = Query("English")):
    """Lab upload with tracking"""
    try:
        contents = await file.read()
        is_pdf = file.content_type == "application/pdf"
        
        print(f"\n📄 Lab: {file.filename} ({language})")
        
        result = lab_parser.process_lab_report(contents, is_pdf)
        ai_analyses = ai_lab_analyzer.analyze_full_report_text(result["extracted_text"], language)
        
        data_collector.save_lab_report(contents, file.filename, ai_analyses, language)
        analytics_tracker.track_lab_analysis(language)
        
        print(f"✅ {len(ai_analyses)} tests\n")
        
        return JSONResponse({
            "success": True,
            "test_count": len(ai_analyses),
            "ai_analysis": ai_analyses
        })
    except Exception as e:
        print(f"❌ {e}")
        raise HTTPException(500, str(e))


# ==================== X-RAY ====================

@app.post("/upload-xray")
async def upload_xray(file: UploadFile = File(...), language: str = Query("English")):
    """X-ray upload with tracking"""
    try:
        contents = await file.read()
        
        print(f"\n🔬 X-ray: {file.filename} ({language})")
        
        xray_analysis = advanced_xray_analyzer.analyze_xray_detailed(contents, language)
        
        data_collector.save_xray(contents, xray_analysis, language)
        analytics_tracker.track_xray_analysis(language)
        
        print(f"✅ X-ray done\n")
        
        return JSONResponse({
            "success": True,
            "xray_analysis": xray_analysis
        })
    except Exception as e:
        print(f"❌ {e}")
        raise HTTPException(500, str(e))


# ==================== COMBINED ====================

@app.post("/analyze-complete")
async def analyze_complete(
    prescription: UploadFile = File(None),
    lab_report: UploadFile = File(None),
    language: str = Query("English")
):
    """Combined analysis"""
    print(f"\n🌐 Combined ({language})")
    
    drugs_info = []
    lab_analysis = []
    
    if prescription:
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
        is_pdf = lab_report.content_type == "application/pdf"
        
        lab_result = lab_parser.process_lab_report(lab_contents, is_pdf)
        lab_analysis = ai_lab_analyzer.analyze_full_report_text(lab_result["extracted_text"], language)
    
    return JSONResponse({
        "drugs": drugs_info,
        "detected_conditions": [],
        "lab_analysis": lab_analysis
    })


# ==================== VOICE ====================

@app.post("/generate-audio")
async def generate_audio(text: str, language: str = "English"):
    """Audio generation with tracking"""
    try:
        print(f"🔊 Audio ({language})")
        
        audio_path = voice_generator.text_to_speech(text, language)
        
        if audio_path and os.path.exists(audio_path):
            analytics_tracker.track_voice_usage("audio", language)
            return FileResponse(audio_path, media_type="audio/mpeg", filename=f"audio_{language}.mp3")
        
        raise HTTPException(500, "Audio failed")
    except Exception as e:
        raise HTTPException(500, str(e))


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
    """Submit feedback"""
    try:
        feedback_id = feedback_collector.save_feedback({
            'rating': rating,
            'comments': comments,
            'feature_used': feature_used,
            'language': language,
            'email': email,
            'feedback_type': feedback_type
        })
        
        return JSONResponse({
            'success': True,
            'message': 'Thank you for your feedback!',
            'feedback_id': feedback_id
        })
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/feedback-stats")
def get_feedback_stats():
    """Feedback statistics"""
    return JSONResponse(feedback_collector.get_statistics())


@app.get("/all-feedback")
def get_all_feedback():
    """All feedback"""
    return JSONResponse({'feedback': feedback_collector.get_all_feedback()})


# ==================== ANALYTICS ====================

@app.get("/analytics")
def get_analytics():
    """Usage analytics"""
    return JSONResponse(analytics_tracker.get_statistics())


@app.get("/analytics-report")
def analytics_report():
    """Analytics report"""
    report = analytics_tracker.generate_analytics_report()
    return JSONResponse({"report": report})

# ==================== FEEDBACK ENDPOINTS ====================

@app.post("/submit-feedback")
async def submit_feedback(
    rating: int = Query(..., ge=1, le=5),
    comments: str = Query(""),
    feature_used: str = Query("general"),
    language: str = Query("English"),
    email: str = Query("anonymous"),
    feedback_type: str = Query("general")
):
    """Submit user feedback"""
    try:
        feedback_id = feedback_collector.save_feedback({
            'rating': rating,
            'comments': comments,
            'feature_used': feature_used,
            'language': language,
            'email': email,
            'feedback_type': feedback_type
        })
        
        return JSONResponse({
            'success': True,
            'message': 'Thank you!',
            'feedback_id': feedback_id
        })
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/feedback-stats")
def get_feedback_stats():
    """Feedback statistics"""
    return JSONResponse(feedback_collector.get_statistics())


# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/analytics")
def get_analytics():
    """Usage analytics"""
    return JSONResponse(analytics_tracker.get_statistics())


# ==================== ADMIN ROUTES (PASSWORD PROTECTED) ====================

ADMIN_PASSWORD = "sargam2026"  # Change this!

@app.get("/admin/dashboard", response_class=FileResponse)
async def admin_dashboard(password: str = Query(None)):
    """Admin dashboard"""
    
    if password != ADMIN_PASSWORD:
        return HTMLResponse("""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 100px; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0;">
                <div style="background: white; padding: 40px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                    <h1 style="margin-bottom: 20px;">🔒 Admin Access</h1>
                    <form method="get">
                        <input type="password" name="password" placeholder="Password" 
                               style="padding: 12px 20px; font-size: 1rem; border: 2px solid #4f46e5; border-radius: 8px; margin-right: 10px;">
                        <button type="submit" style="padding: 12px 24px; background: #4f46e5; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
                            Access
                        </button>
                    </form>
                </div>
            </body>
            </html>
        """)
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return HTMLResponse("<h1>Not found</h1>")


@app.get("/admin/export-excel")
async def admin_export_excel(password: str = Query(...)):
    """Export to Excel (admin only)"""
    
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Access denied")
    
    filepath = excel_exporter.export_combined()
    
    if filepath and os.path.exists(filepath):
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(filepath)
        )
    raise HTTPException(500, "Export failed")


@app.get("/admin/analytics-data")
async def admin_analytics_data(password: str = Query(...)):
    """Analytics data (admin only)"""
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    return JSONResponse(analytics_tracker.get_statistics())


@app.get("/admin/feedback-data")
async def admin_feedback_data(password: str = Query(...)):
    """Feedback data (admin only)"""
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    return JSONResponse({
        'stats': feedback_collector.get_statistics(),
        'all_feedback': feedback_collector.get_all_feedback()
    })


@app.get("/admin/dataset-data")
async def admin_dataset_data(password: str = Query(...)):
    """Dataset data (admin only)"""
    if password != ADMIN_PASSWORD:
        raise HTTPException(403, "Denied")
    return JSONResponse(data_collector.get_statistics())

# ==================== DATASET ====================

@app.get("/dataset-stats")
def dataset_stats():
    """Dataset statistics"""
    return JSONResponse(data_collector.get_statistics())


@app.get("/export-dataset-summary")
def dataset_summary():
    """Dataset summary"""
    return JSONResponse({"summary": data_collector.export_dataset_summary()})


# ==================== UTILITY ====================

@app.post("/analyze-labs")
def analyze_labs(query: LabQuery):
    """Lab utility"""
    language = query.language or "English"
    test_results = [{"test_name": r.test_name, "value": r.value, "unit": ""} for r in query.results]
    analyses = ai_lab_analyzer.analyze_full_report(test_results, language)
    return JSONResponse({"lab_analysis": analyses})


@app.get("/drug/{drug_name}")
def get_drug_info(drug_name: str):
    """Single drug info"""
    drug_info = drug_service.get_drug_info(drug_name)
    if drug_info["confidence"] == "none":
        raise HTTPException(404, "Not found")
    return JSONResponse(drug_info)


@app.get("/database-stats")
def database_stats():
    """Drug database stats"""
    return JSONResponse(drug_service.get_stats())


# ==================== STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print(" "*20 + "🏥 MediSimplify")
    print(" "*10 + "AI-Powered Medical Report Analyzer")
    print("="*70)
    print("\n📍 App:       http://127.0.0.1:8000/")
    print("📚 Docs:      http://127.0.0.1:8000/docs")
    print("📊 Analytics: http://127.0.0.1:8000/analytics")
    print("💬 Feedback:  http://127.0.0.1:8000/feedback-stats")
    print("\n" + "="*70)
    print("By: Sargam Chicholikar | Feb 2026 | MIT License")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, timeout_keep_alive=120)