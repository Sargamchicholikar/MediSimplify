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
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import time
from data_collector import data_collector
from drug_database import DRUG_COMBINATIONS, ABBREVIATIONS
from drug_service import drug_service
from lab_database import LAB_TESTS
from ocr_module import PrescriptionOCR, LabReportParser
from ai_lab_analyzer import ai_lab_analyzer
from drug_translator import drug_translator  # NEW!
from advanced_xray_vision import advanced_xray_analyzer
from voice_generator import voice_generator
from fastapi.responses import FileResponse
from fastapi.responses import FileResponse, HTMLResponse
import os


app = FastAPI(title="Medical Simplifier API")

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
print("Initializing system...")
print("="*60)
ocr_engine = PrescriptionOCR()
lab_parser = LabReportParser()
print("✅ All systems ready!\n")

# Models
class DrugQuery(BaseModel):
    drug_names: List[str]
    language: Optional[str] = "English"

class LabResult(BaseModel):
    test_name: str
    value: float

class LabQuery(BaseModel):
    results: List[LabResult]
    language: Optional[str] = "English"

class DrugInfo(BaseModel):
    name: str
    treats: str
    explanation: str
    dosage: str
    frequency: str
    warnings: str

class ConditionInfo(BaseModel):
    condition: str
    explanation: str


def validate_drug_sync(drug_name):
    return drug_service.get_drug_info(drug_name)


@app.get("/")
def root():
    return {"message": "Medical Simplifier API - Multi-language support!"}


@app.post("/analyze-drugs")
def analyze_drugs(query: DrugQuery):
    """Analyze drugs with language support"""
    
    language = query.language or "English"
    
    print(f"\n🚀 Analyzing {len(query.drug_names)} drugs...")
    print(f"🌐 Language: {language}")
    
    drugs_info = []
    validated_drugs = []
    
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
    
    # Translate if not English
    if language != "English":
        print(f"🌐 Translating drugs to {language}...")
        drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    detected_conditions = []
    drug_set = frozenset(validated_drugs)
    
    for combo, info in DRUG_COMBINATIONS.items():
        if combo.issubset(drug_set):
            detected_conditions.append({
                "condition": info["condition"],
                "explanation": info["explanation"]
            })
    
    return JSONResponse(content={
        "drugs": drugs_info,
        "detected_conditions": detected_conditions
    }, status_code=200)


@app.post("/analyze-labs")
def analyze_labs(query: LabQuery):
    """Analyze labs"""
    
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
    drug_info = drug_service.get_drug_info(drug_name)
    if drug_info["confidence"] == "none":
        raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse(content=drug_info, status_code=200)


@app.get("/database-stats")
def get_database_stats():
    return JSONResponse(content=drug_service.get_stats(), status_code=200)


@app.post("/upload-prescription")
async def upload_prescription(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Images only")
    
    try:
        contents = await file.read()
        result = ocr_engine.process_prescription(contents)
        
        # SAVE TO DATASET (NEW!)
        data_collector.save_prescription(
            image_bytes=contents,
            extracted_drugs=result["found_drugs"],
            analysis_result={"drugs": result["found_drugs"]},
            language="English"
        )
        
        return JSONResponse(content={
            "success": True,
            "found_drugs": result["found_drugs"],
            "drug_count": len(result["found_drugs"])
        }, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-lab-report")
async def upload_lab_report(
    file: UploadFile = File(...),
    language: str = Query("English")
):
    """Upload lab with data collection"""
    
    try:
        contents = await file.read()
        is_pdf = file.content_type == "application/pdf"
        
        print(f"\n📄 Lab: {file.filename} (Lang: {language})")
        
        result = lab_parser.process_lab_report(contents, is_pdf)
        extracted_text = result["extracted_text"]
        
        ai_analyses = ai_lab_analyzer.analyze_full_report_text(extracted_text, language=language)
        
        # SAVE TO DATASET (NEW!)
        data_collector.save_lab_report(
            file_bytes=contents,
            file_type="pdf" if is_pdf else "image",
            extracted_tests=ai_analyses,
            ai_analysis=ai_analyses,
            language=language
        )
        
        print(f"✅ Analyzed {len(ai_analyses)} tests\n")
        
        return JSONResponse(content={
            "success": True,
            "test_count": len(ai_analyses),
            "ai_analysis": ai_analyses
        }, status_code=200)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-complete")
async def analyze_complete(
    prescription: UploadFile = File(None),
    lab_report: UploadFile = File(None),
    language: str = Query("English")
):
    """Complete analysis with language"""
    
    print(f"\n🌐 Language: {language}")
    
    drug_candidates = []
    drugs_info = []
    lab_analysis = []
    
    # Prescription
    if prescription:
        pres_contents = await prescription.read()
        pres_result = ocr_engine.process_prescription(pres_contents)
        drug_candidates = pres_result["found_drugs"]
        
        # Validate drugs
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
        
        # Translate drugs
        if language != "English":
            drugs_info = drug_translator.translate_multiple_drugs(drugs_info, language)
    
    # Lab report
    if lab_report:
        lab_contents = await lab_report.read()
        is_pdf = lab_report.content_type == "application/pdf"
        
        lab_result = lab_parser.process_lab_report(lab_contents, is_pdf)
        extracted_text = lab_result["extracted_text"]
        
        # AI in selected language
        lab_analysis = ai_lab_analyzer.analyze_full_report_text(extracted_text, language=language)
    
    detected_conditions = []
    
    return JSONResponse(content={
        "drugs": drugs_info,
        "detected_conditions": detected_conditions,
        "lab_analysis": lab_analysis
    }, status_code=200)

@app.post("/upload-xray")
async def upload_xray(
    file: UploadFile = File(...),
    language: str = Query("English")
):
    """Upload X-ray with data collection"""
    
    try:
        contents = await file.read()
        
        print(f"\n🔬 X-ray: {file.filename} (Lang: {language})")
        
        xray_analysis = advanced_xray_analyzer.analyze_xray_detailed(contents, language)
        
        # SAVE TO DATASET (NEW!)
        data_collector.save_xray(
            image_bytes=contents,
            ai_analysis=xray_analysis,
            language=language
        )
        
        print(f"✅ X-ray analyzed\n")
        
        return JSONResponse(content={
            "success": True,
            "xray_analysis": xray_analysis
        }, status_code=200)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate-audio")
async def generate_audio(text: str, language: str = "English"):
    """Generate audio from text"""
    
    try:
        print(f"🔊 Audio request: {len(text)} chars in {language}")
        
        # Generate audio
        audio_path = voice_generator.text_to_speech(text, language)
        
        if audio_path and os.path.exists(audio_path):
            print(f"✅ Sending audio file: {audio_path}")
            
            return FileResponse(
                audio_path,
                media_type="audio/mpeg",
                filename=f"medical_explanation_{language}.mp3"
            )
        else:
            raise HTTPException(status_code=500, detail="Audio generation failed")
    
    except Exception as e:
        print(f"❌ Audio endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))   

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


@app.get("/about", response_class=HTMLResponse)
async def about_page():
    """Serve about page"""
    
    # Build path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    about_path = os.path.join(base_dir, "..", "frontend", "about.html")
    
    print(f"Looking for about.html at: {about_path}")
    print(f"Exists: {os.path.exists(about_path)}")
    
    try:
        with open(about_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback: check alternate location
        alt_path = os.path.join(os.getcwd(), "frontend", "about.html")
        print(f"Trying alternate: {alt_path}")
        
        try:
            with open(alt_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        except:
            return HTMLResponse(
                f"<h1>File not found</h1>"
                f"<p>Looking for: {about_path}</p>"
                f"<p>Current dir: {os.getcwd()}</p>"
                f"<p>Please ensure about.html is in frontend/ folder</p>"
            )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, timeout_keep_alive=120)