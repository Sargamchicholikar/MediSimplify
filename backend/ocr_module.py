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

import easyocr
import cv2
import numpy as np
from fuzzywuzzy import fuzz
import re

class PrescriptionOCR:
    def __init__(self):
        print("Loading OCR model...")
        self.reader = easyocr.Reader(['en'], gpu=False)
        
        # NO MORE local drug database!
        # Build smart filters instead
        self._build_filters()
        
        print("✅ OCR ready!")
    
    def _build_filters(self):
        """Build medication patterns and blacklists"""
        
        # Drug name patterns (common endings)
        self.drug_endings = [
            'pine', 'pril', 'sartan', 'olol', 'statin', 
            'cillin', 'mycin', 'floxacin', 'zole', 'prazole',
            'tidine', 'formin', 'zine', 'mide', 'done',
            'mab', 'ast', 'kind', 'clar', 'cal', 'lin',
            'ride', 'ine', 'ide', 'ate'
        ]
        
        # Drug prefixes
        self.drug_prefixes = [
            'levo', 'dex', 'hydro', 'pro', 'anti', 'met',
            'cef', 'ator', 'simva', 'amlod', 'abci', 'vomi',
            'zoc', 'gesta', 'isox', 'doxyl', 'pyrid', 'clari'
        ]
        
        # Words that are NEVER drugs
        self.blacklist = {
            'prescription', 'medicine', 'dosage', 'duration', 'advice',
            'diagnosis', 'clinical', 'findings', 'complaints', 'sample',
            'name', 'patient', 'age', 'gender', 'male', 'female',
            'address', 'phone', 'weight', 'height', 'blood', 'pressure',
            'medical', 'centre', 'center', 'hospital', 'clinic',
            'date', 'time', 'timing', 'morning', 'night', 'evening',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'closed', 'follow', 'signature', 'label', 'refill',
            'outside', 'inside', 'digest', 'boiled', 'entering',
            'fever', 'chills', 'headache', 'chief', 'required'
        }
    
    def process_prescription(self, image_bytes):
        """Extract drug names from prescription image"""
        try:
            # Convert to image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # OCR
            print("🔍 Running OCR...")
            results = self.reader.readtext(img)
            
            # Get text
            text_blocks = [r[1] for r in results]
            full_text = ' '.join(text_blocks)
            
            print(f"📄 Extracted {len(text_blocks)} text blocks")
            
            # Extract candidates
            candidates = self._extract_candidates(text_blocks)
            
            print(f"💊 Drug candidates: {candidates}")
            
            # Limit to 8 for FDA API
            if len(candidates) > 8:
                print(f"⚠️ Limiting candidates from {len(candidates)} to 8")
                candidates = candidates[:8]
            
            return {
                "extracted_text": full_text,
                "found_drugs": candidates
            }
            
        except Exception as e:
            print(f"❌ OCR Error: {e}")
            return {"extracted_text": "", "found_drugs": []}
    
    def _extract_candidates(self, text_blocks):
        """Extract potential drug names"""
        candidates = []
        
        for block in text_blocks:
            cleaned = self._clean_text(block)
            
            if not cleaned:
                continue
            
            words = cleaned.split()
            
            for word in words:
                if self._is_drug_candidate(word):
                    if word not in candidates:
                        candidates.append(word)
        
        return candidates
    
    def _clean_text(self, text):
        """Clean text block"""
        text = text.lower().strip()
        
        # Remove medication prefixes
        text = re.sub(r'\b(tab\.?|cap\.?|syp\.?|inj\.?|dr\.?|susp\.?)\s*', '', text)
        
        # Remove dosages
        text = re.sub(r'\d+\s*(?:mg|mcg|ml|g|/\d+)', '', text)
        
        # Remove frequency
        text = re.sub(r'\b(bid|tid|qid|od|sos|stat|prn|tds|x\d+d?)\b', '', text)
        
        # Remove numbers and special chars
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        return ' '.join(text.split())
    
    def _is_drug_candidate(self, word):
        """Is this likely a drug name?"""
        word = word.lower().strip()
        
        # Length check
        if len(word) < 5 or len(word) > 20:
            return False
        
        # Format check
        if not re.match(r'^[a-z]+(?:-[a-z]+)?$', word):
            return False
        
        # Blacklist
        if word in self.blacklist:
            return False
        
        # MUST match drug patterns
        # Check endings
        for ending in self.drug_endings:
            if word.endswith(ending) and len(word) > len(ending) + 2:
                return True
        
        # Check prefixes
        for prefix in self.drug_prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                return True
        
        # Doesn't match drug patterns
        return False


class LabReportParser:
    def __init__(self):
        from lab_database import LAB_TESTS
        self.known_tests = list(LAB_TESTS.keys())
    
    def extract_from_pdf(self, pdf_bytes):
        import PyPDF2
        import io
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"PDF error: {e}")
            return ""
    
    def parse_values(self, text):
        results = []
        lines = text.split('\n')
        for line in lines:
            for test_name in self.known_tests:
                if test_name.lower() in line.lower():
                    numbers = re.findall(r'\d+\.?\d*', line)
                    if numbers:
                        value = float(numbers[0])
                        results.append({"test_name": test_name, "value": value})
                        print(f"Found test: {test_name} = {value}")
                        break
        return results
    
    def process_lab_report(self, file_bytes, is_pdf):
        if is_pdf:
            text = self.extract_from_pdf(file_bytes)
        else:
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(file_bytes)
            text = ' '.join([r[1] for r in results])
        
        test_results = self.parse_values(text)
        return {"extracted_text": text, "test_results": test_results}