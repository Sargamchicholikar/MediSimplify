"""
Medical Data Collector
Collects and organizes user-uploaded reports for dataset creation
Segregated by type: Prescriptions, Lab Reports, X-Rays

Copyright (c) 2026 Sargam Chicholikar
Created: February 2026
"""

import os
import json
import shutil
from datetime import datetime
import hashlib

class MedicalDataCollector:
    def __init__(self):
        """Initialize data collector with segregated folders"""
        
        # Base directory for collected data
        self.base_dir = "collected_data"
        
        # Segregated folders by report type
        self.prescription_dir = os.path.join(self.base_dir, "prescriptions")
        self.lab_report_dir = os.path.join(self.base_dir, "lab_reports")
        self.xray_dir = os.path.join(self.base_dir, "xrays")
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        
        # Create all directories
        for directory in [self.prescription_dir, self.lab_report_dir, 
                         self.xray_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Statistics file
        self.stats_file = os.path.join(self.base_dir, "collection_stats.json")
        self._initialize_stats()
        
        print("✅ Data Collector ready (Privacy-preserving dataset creation)")
    
    def _initialize_stats(self):
        """Initialize or load statistics"""
        if not os.path.exists(self.stats_file):
            stats = {
                "total_prescriptions": 0,
                "total_lab_reports": 0,
                "total_xrays": 0,
                "total_analyses": 0,
                "languages_used": {},
                "started_on": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
    
    def save_prescription(self, image_bytes, extracted_drugs, analysis_result, language="English"):
        """
        Save prescription data for dataset
        
        Args:
            image_bytes: Raw image data
            extracted_drugs: List of drug names extracted
            analysis_result: Complete analysis from API
            language: User's selected language
        
        Returns:
            unique_id: ID of saved record
        """
        try:
            # Generate unique ID with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(image_bytes).hexdigest()[:8]
            unique_id = f"presc_{timestamp}_{file_hash}"
            
            # Save image
            image_path = os.path.join(self.prescription_dir, f"{unique_id}.jpg")
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Save metadata (anonymized - no patient info!)
            metadata = {
                "id": unique_id,
                "type": "prescription",
                "timestamp": timestamp,
                "language": language,
                "extracted_drugs": extracted_drugs,
                "drug_count": len(extracted_drugs),
                "validated_drugs": len(analysis_result.get('drugs', [])),
                "conditions_detected": len(analysis_result.get('detected_conditions', [])),
                "image_file": f"{unique_id}.jpg",
                "collection_date": datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(self.metadata_dir, f"{unique_id}_meta.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update statistics
            self._update_stats("prescription", language)
            
            print(f"💾 Saved prescription: {unique_id}")
            
            return unique_id
            
        except Exception as e:
            print(f"⚠️ Data collection error: {e}")
            return None
    
    def save_lab_report(self, file_bytes, file_type, extracted_tests, ai_analysis, language="English"):
        """
        Save lab report data for dataset
        
        Args:
            file_bytes: Raw file data (PDF or image)
            file_type: "pdf" or "image"
            extracted_tests: List of test results extracted
            ai_analysis: AI analysis results
            language: User's selected language
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
            unique_id = f"lab_{timestamp}_{file_hash}"
            
            # Save file with appropriate extension
            ext = ".pdf" if file_type == "pdf" else ".jpg"
            file_path = os.path.join(self.lab_report_dir, f"{unique_id}{ext}")
            
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            # Save metadata
            metadata = {
                "id": unique_id,
                "type": "lab_report",
                "timestamp": timestamp,
                "language": language,
                "file_type": file_type,
                "tests_extracted": len(extracted_tests),
                "test_names": [t.get('test', 'Unknown') for t in extracted_tests],
                "file": f"{unique_id}{ext}",
                "collection_date": datetime.now().isoformat()
            }
            
            # Save full AI analysis separately
            analysis_path = os.path.join(self.lab_report_dir, f"{unique_id}_analysis.json")
            with open(analysis_path, 'w') as f:
                json.dump(ai_analysis, f, indent=2)
            
            metadata_path = os.path.join(self.metadata_dir, f"{unique_id}_meta.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self._update_stats("lab_report", language)
            
            print(f"💾 Saved lab report: {unique_id}")
            
            return unique_id
            
        except Exception as e:
            print(f"⚠️ Lab collection error: {e}")
            return None
    
    def save_xray(self, image_bytes, ai_analysis, language="English"):
        """
        Save X-ray data with AI analysis for dataset
        
        Args:
            image_bytes: Raw X-ray image data
            ai_analysis: Complete AI analysis result
            language: User's selected language
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(image_bytes).hexdigest()[:8]
            unique_id = f"xray_{timestamp}_{file_hash}"
            
            # Save image
            image_path = os.path.join(self.xray_dir, f"{unique_id}.jpg")
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Save metadata
            metadata = {
                "id": unique_id,
                "type": "xray",
                "timestamp": timestamp,
                "language": language,
                "ai_analysis": {
                    "body_part": ai_analysis.get('body_part', 'Unknown'),
                    "has_fracture": ai_analysis.get('has_fracture', False),
                    "fracture_type": ai_analysis.get('fracture_type', 'N/A'),
                    "fracture_location": ai_analysis.get('fracture_location', 'N/A'),
                    "recovery_time": ai_analysis.get('recovery_time', 'N/A'),
                    "likely_cause": ai_analysis.get('likely_cause', 'N/A')
                },
                "image_file": f"{unique_id}.jpg",
                "collection_date": datetime.now().isoformat()
            }
            
            # Save full AI analysis
            analysis_path = os.path.join(self.xray_dir, f"{unique_id}_analysis.json")
            with open(analysis_path, 'w') as f:
                json.dump(ai_analysis, f, indent=2)
            
            metadata_path = os.path.join(self.metadata_dir, f"{unique_id}_meta.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self._update_stats("xray", language)
            
            print(f"💾 Saved X-ray: {unique_id}")
            
            return unique_id
            
        except Exception as e:
            print(f"⚠️ X-ray collection error: {e}")
            return None
    
    def _update_stats(self, data_type, language):
        """Update collection statistics"""
        try:
            # Load current stats
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            # Update counts
            if data_type == "prescription":
                stats["total_prescriptions"] = stats.get("total_prescriptions", 0) + 1
            elif data_type == "lab_report":
                stats["total_lab_reports"] = stats.get("total_lab_reports", 0) + 1
            elif data_type == "xray":
                stats["total_xrays"] = stats.get("total_xrays", 0) + 1
            
            stats["total_analyses"] = stats.get("total_analyses", 0) + 1
            
            # Track language usage
            if "languages_used" not in stats:
                stats["languages_used"] = {}
            
            if language not in stats["languages_used"]:
                stats["languages_used"][language] = 0
            stats["languages_used"][language] += 1
            
            # Update timestamp
            stats["last_updated"] = datetime.now().isoformat()
            
            # Save updated stats
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Stats update error: {e}")
    
    def get_statistics(self):
        """Get collection statistics"""
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "total_prescriptions": 0,
                "total_lab_reports": 0,
                "total_xrays": 0,
                "total_analyses": 0
            }
    
    def export_dataset_summary(self):
        """
        Generate dataset summary report
        Useful for documentation and research papers
        """
        stats = self.get_statistics()
        
        summary = f"""
{'='*70}
MediSimplify - Collected Dataset Summary
{'='*70}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DATASET STATISTICS:
------------------
Total Prescriptions Collected: {stats.get('total_prescriptions', 0)}
Total Lab Reports Collected:   {stats.get('total_lab_reports', 0)}
Total X-Rays Collected:        {stats.get('total_xrays', 0)}
Total Analyses Performed:      {stats.get('total_analyses', 0)}

LANGUAGE DISTRIBUTION:
---------------------
"""
        
        for lang, count in sorted(stats.get('languages_used', {}).items(), 
                                  key=lambda x: x[1], reverse=True):
            summary += f"{lang:15} : {count:4} analyses\n"
        
        summary += f"""
COLLECTION PERIOD:
-----------------
Started:      {stats.get('started_on', 'Unknown')}
Last Updated: {stats.get('last_updated', 'Unknown')}

DATASET STRUCTURE:
-----------------
collected_data/
├── prescriptions/    ({stats.get('total_prescriptions', 0)} samples)
├── lab_reports/      ({stats.get('total_lab_reports', 0)} samples)
├── xrays/            ({stats.get('total_xrays', 0)} samples)
└── metadata/         (JSON files with annotations)

{'='*70}
Dataset collected by: Sargam Chicholikar
Institution: Bharati Vidyapeeth University, Pune
Purpose: Research and model improvement
{'='*70}
"""
        
        # Save summary
        summary_path = os.path.join(self.base_dir, "DATASET_SUMMARY.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(summary)
        
        return summary


# Initialize global collector
data_collector = MedicalDataCollector()