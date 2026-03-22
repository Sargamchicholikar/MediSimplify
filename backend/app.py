"""
AI Medical Report Simplifier
Copyright (c) 2026 Sargam Chicholikar
Licensed under MIT License

Original Author: Sargam Chicholikar
Email: work.sargam@gmail.com
GitHub: https://github.com/Sargamchicholikar
LinkedIn: https://linkedin.com/in/sargam-chicholikar
Created: February 2026

This file is part of the AI Medical Report Simplifier project.
For full license information, see LICENSE file in project root.
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
from analytics_tracker import analytics_tracker  # NEW!
from drug_database import DRUG_COMBINATIONS, ABBREVIATIONS
from drug_service import drug_service
from lab_database import LAB_TESTS
from ocr_module import PrescriptionOCR, LabReportParser
from ai_lab_analyzer import ai_lab_analyzer
from drug_translator import drug_translator
from advanced_xray_vision import advanced_xray_analyzer
from voice_generator import voice_generator


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
    """Helper function for parallel drug validation"""
    return drug_service.get_drug_info(drug_name)


# ==================== FRONTEND ROUTES ====================

@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve main application page"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return HTMLResponse("<h1>MediSimplify</h1><p>Frontend not found</p>")


@app.get("/about", response_class=HTMLResponse)
async def about_page():
    """Serve about page (local only)"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    about_path = os.path.join(base_dir, "..", "frontend", "about.html")
    
    try:
        with open(about_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>About</h1><p>Available in local version only</p>")


# ==================== DRUG ANALYSIS ====================

@app.post("/analyze-drugs")
def analyze_drugs(query: DrugQuery):
    """Analyze manually entered drugs with tracking"""
    
    language = query.language or "English"
    
    print(f"\n🚀 Analyzing {len(query.drug_names)} drugs...")
    print(f"🌐 Language: {language}")
    
    drugs_info = []
    validated_drugs = []
    
    # Parallel validation
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_drug = {
            executor.submit(validate_drug_sync, drug_name): drug_name 
            for drug_name in query.drug_names
        }
        
        for future in future_to_drug:
            drug_name = future_to_drug[future]
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
    
    # Translate if needed
    if language != "English":
        print(f"🌐 Translating to {language}...")
        drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    # Detect conditions
    detected_conditions = []
    drug_set = frozenset(validated_drugs)
    
    for combo, info in DRUG_COMBINATIONS.items():
        if combo.issubset(drug_set):
            detected_conditions.append({
                "condition": info["condition"],
                "explanation": info["explanation"]
            })
    
    # TRACK USAGE (NEW!)
    analytics_tracker.track_prescription_analysis(
        language=language,
        is_upload=False  # Manual typing
    )
    
    return JSONResponse(content={
        "drugs": drugs_info,
        "detected_conditions": detected_conditions
    }, status_code=200)


# ==================== PRESCRIPTION UPLOAD ====================

@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    """Upload prescription image with tracking"""
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Images only")
    
    try:
        contents = await file.read()
        result = ocr_engine.process_prescription(contents)
        
        # Save to dataset
        data_collector.save_prescription(
            image_bytes=contents,
            extracted_drugs=result["found_drugs"],
            language="English"
        )
        
        # TRACK USAGE (NEW!)
        analytics_tracker.track_prescription_analysis(
            language="English",
            is_upload=True  # Image upload
        )
        
        return JSONResponse(content={
            "success": True,
            "found_drugs": result["found_drugs"],
            "drug_count": len(result["found_drugs"])
        }, status_code=200)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LAB REPORT UPLOAD ====================

@app.post("/upload-lab-report")
async def upload_lab_report(
    file: UploadFile = File(...),
    language: str = Query("English")
):
    """Upload lab report with tracking"""
    
    try:
        contents = await file.read()
        is_pdf = file.content_type == "application/pdf"
        
        print(f"\n📄 Lab: {file.filename} (Lang: {language})")
        
        # Parse and analyze
        result = lab_parser.process_lab_report(contents, is_pdf)
        extracted_text = result["extracted_text"]
        ai_analyses = ai_lab_analyzer.analyze_full_report_text(extracted_text, language=language)
        
        # Save to dataset
        data_collector.save_lab_report(
            file_bytes=contents,
            filename=file.filename,
            ai_analysis=ai_analyses,
            language=language
        )
        
        # TRACK USAGE (NEW!)
        analytics_tracker.track_lab_analysis(language=language)
        
        print(f"✅ Analyzed {len(ai_analyses)} tests\n")
        
        return JSONResponse(content={
            "success": True,
            "test_count": len(ai_analyses),
            "ai_analysis": ai_analyses
        }, status_code=200)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== X-RAY UPLOAD ====================

@app.post("/upload-xray")
async def upload_xray(
    file: UploadFile = File(...),
    language: str = Query("English")
):
    """Upload X-ray with tracking"""
    
    try:
        contents = await file.read()
        
        print(f"\n🔬 X-ray: {file.filename} (Lang: {language})")
        
        # AI analysis
        xray_analysis = advanced_xray_analyzer.analyze_xray_detailed(contents, language)
        
        # Save to dataset
        data_collector.save_xray(
            image_bytes=contents,
            ai_analysis=xray_analysis,
            language=language
        )
        
        # TRACK USAGE (NEW!)
        analytics_tracker.track_xray_analysis(language=language)
        
        print(f"✅ X-ray analyzed\n")
        
        return JSONResponse(content={
            "success": True,
            "xray_analysis": xray_analysis
        }, status_code=200)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMBINED ANALYSIS ====================

@app.post("/analyze-complete")
async def analyze_complete(
    prescription: UploadFile = File(None),
    lab_report: UploadFile = File(None),
    language: str = Query("English")
):
    """Complete analysis (no duplicate data saving)"""
    
    print(f"\n🌐 Combined analysis in {language}")
    
    drugs_info = []
    lab_analysis = []
    
    # Prescription
    if prescription:
        pres_contents = await prescription.read()
        pres_result = ocr_engine.process_prescription(pres_contents)
        drug_candidates = pres_result["found_drugs"]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(validate_drug_sync, d): d for d in drug_candidates}
            
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
    
    # Lab report
    if lab_report:
        lab_contents = await lab_report.read()
        is_pdf = lab_report.content_type == "application/pdf"
        
        lab_result = lab_parser.process_lab_report(lab_contents, is_pdf)
        extracted_text = lab_result["extracted_text"]
        lab_analysis = ai_lab_analyzer.analyze_full_report_text(extracted_text, language=language)
    
    detected_conditions = []
    
    return JSONResponse(content={
        "drugs": drugs_info,
        "detected_conditions": detected_conditions,
        "lab_analysis": lab_analysis
    }, status_code=200)


# ==================== VOICE GENERATION ====================

@app.post("/generate-audio")
async def generate_audio(text: str, language: str = "English"):
    """Generate audio with tracking"""
    
    try:
        print(f"🔊 Audio: {len(text)} chars in {language}")
        
        audio_path = voice_generator.text_to_speech(text, language)
        
        if audio_path and os.path.exists(audio_path):
            
            # TRACK VOICE USAGE (NEW!)
            analytics_tracker.track_voice_usage(
                report_type="audio",
                language=language
            )
            
            return FileResponse(
                audio_path,
                media_type="audio/mpeg",
                filename=f"explanation_{language}.mp3"
            )
        else:
            raise HTTPException(status_code=500, detail="Audio failed")
            
    except Exception as e:
        print(f"❌ Audio error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ENDPOINTS (NEW!) ====================

@app.get("/analytics")
def get_analytics():
    """Get usage analytics"""
    stats = analytics_tracker.get_statistics()
    return JSONResponse(content=stats, status_code=200)


@app.get("/analytics-report")
def get_analytics_report():
    """Generate detailed analytics report"""
    report = analytics_tracker.generate_analytics_report()
    return JSONResponse(content={"report": report}, status_code=200)


# ==================== DATASET MANAGEMENT ====================

@app.get("/dataset-stats")
def get_dataset_stats():
    """Get collected dataset statistics"""
    stats = data_collector.get_statistics()
    return JSONResponse(content=stats, status_code=200)


@app.get("/export-dataset-summary")
def export_dataset_summary():
    """Generate dataset summary report"""
    summary = data_collector.export_dataset_summary()
    return JSONResponse(content={"summary": summary}, status_code=200)


# ==================== LEGACY/UTILITY ENDPOINTS ====================

@app.post("/analyze-labs")
def analyze_labs(query: LabQuery):
    """Analyze lab results (utility endpoint)"""
    
    language = query.language or "English"
    
    print(f"\n🧪 Analyzing {len(query.results)} tests in {language}...")
    
    test_results = [
        {"test_name": r.test_name, "value": r.value, "unit": ""}
        for r in query.results
    ]
    
    analyses = ai_lab_analyzer.analyze_full_report(test_results, language=language)
    
    return JSONResponse(content={"lab_analysis": analyses}, status_code=200)


@app.get("/drug/{drug_name}")
def get_drug_info(drug_name: str):
    """Get info for single drug"""
    drug_info = drug_service.get_drug_info(drug_name)
    if drug_info["confidence"] == "none":
        raise HTTPException(status_code=404, detail="Drug not found")
    return JSONResponse(content=drug_info, status_code=200)


@app.get("/database-stats")
def get_database_stats():
    """Get drug database statistics"""
    return JSONResponse(content=drug_service.get_stats(), status_code=200)


# ==================== SERVER STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print(" "*20 + "🏥 MediSimplify")
    print(" "*10 + "AI-Powered Medical Report Analyzer")
    print("="*70)
    print("\n📍 Application:  http://127.0.0.1:8000/")
    print("📚 API Docs:     http://127.0.0.1:8000/docs")
    print("ℹ️  About Page:   http://127.0.0.1:8000/about")
    print("📊 Dataset:      http://127.0.0.1:8000/dataset-stats")
    print("📈 Analytics:    http://127.0.0.1:8000/analytics")
    print("\n" + "="*70)
    print("Created by: Sargam Chicholikar | February 2026")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, timeout_keep_alive=120)