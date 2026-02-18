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

"""
FDA OpenAPI Integration with Fuzzy Matching
"""

import requests
import re
from functools import lru_cache
from fuzzywuzzy import fuzz

class FDADrugAPI:
    BASE_URL = "https://api.fda.gov/drug"
    
    @lru_cache(maxsize=500)
    def search_drug(self, drug_name):
        """
        Search FDA with fuzzy matching
        Handles OCR mistakes automatically
        """
        try:
            # First try exact search
            result = self._exact_search(drug_name)
            if result:
                return result
            
            # If not found, try fuzzy search
            return self._fuzzy_search(drug_name)
            
        except Exception as e:
            print(f"❌ FDA API error: {e}")
            return None
    
    def _exact_search(self, drug_name):
        """Try exact match first"""
        try:
            url = f"{self.BASE_URL}/label.json"
            search_query = f'openfda.brand_name:"{drug_name}" openfda.generic_name:"{drug_name}"'
            
            params = {"search": search_query, "limit": 1}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    print(f"✅ Exact match found: {drug_name}")
                    return self._parse_fda_response(data["results"][0], drug_name)
            
            return None
            
        except:
            return None
    
    def _fuzzy_search(self, drug_name):
        """
        Fuzzy search with 75% threshold
        Handles OCR mistakes like: befaloc → betaloc
        """
        try:
            print(f"🔍 Fuzzy searching FDA for: {drug_name}")
            
            # Use first 4-5 characters for wildcard search
            prefix_len = min(5, max(4, len(drug_name) - 2))
            prefix = drug_name[:prefix_len]
            
            url = f"{self.BASE_URL}/label.json"
            
            # Wildcard search
            search_query = f'openfda.brand_name:"{prefix}"* openfda.generic_name:"{prefix}"*'
            params = {"search": search_query, "limit": 30}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("results"):
                    best_match = None
                    best_score = 0
                    
                    # Check all results
                    for result in data["results"]:
                        openfda = result.get("openfda", {})
                        
                        # Collect all possible names
                        all_names = []
                        if openfda.get("brand_name"):
                            all_names.extend(openfda["brand_name"])
                        if openfda.get("generic_name"):
                            all_names.extend(openfda["generic_name"])
                        
                        # Find best fuzzy match
                        for name in all_names:
                            score = fuzz.ratio(drug_name.lower(), name.lower())
                            if score > best_score:
                                best_score = score
                                best_match = (result, name)
                    
                    # Accept if 75%+ similarity
                    if best_match and best_score >= 75:
                        print(f"✅ FDA fuzzy match: '{drug_name}' → '{best_match[1]}' ({best_score}%)")
                        return self._parse_fda_response(best_match[0], best_match[1])
                    else:
                        print(f"❌ No good match found (best: {best_score}%)")
            
            return None
            
        except Exception as e:
            print(f"⚠️ Fuzzy search error: {e}")
            return None
    
    def _parse_fda_response(self, result, drug_name):
        """Parse FDA response into our format"""
        return {
            "name": drug_name.title(),
            "category": self._get_category(result),
            "treats": self._get_indications(result),
            "simple_explanation": self._get_description(result),
            "common_dosage": self._get_dosage(result),
            "frequency": self._get_frequency(result),
            "side_effects": self._get_side_effects(result),
            "warnings": self._get_warnings(result),
            "source": "FDA Database",
            "confidence": "high"
        }
    
    def _get_category(self, result):
        """Extract drug category"""
        openfda = result.get("openfda", {})
        if openfda.get("pharm_class_epc"):
            category = openfda["pharm_class_epc"][0]
            category = category.replace("[EPC]", "").strip()
            return category[:100]
        return "Prescription Medication"
    
    def _get_indications(self, result):
        """Extract what the drug treats"""
        indications = result.get("indications_and_usage", [""])
        if indications and indications[0]:
            text = indications[0]
            first_sentence = text.split('.')[0].strip()
            first_sentence = self._simplify_text(first_sentence)
            return first_sentence[:200]
        return "Various medical conditions"
    
    def _get_description(self, result):
        """Extract simple explanation"""
        mechanism = result.get("mechanism_of_action", [""])
        if mechanism and mechanism[0]:
            text = mechanism[0].split('.')[0].strip()
            return self._simplify_text(text)[:200]
        
        pharmacology = result.get("clinical_pharmacology", [""])
        if pharmacology and pharmacology[0]:
            text = pharmacology[0].split('.')[0].strip()
            return self._simplify_text(text)[:200]
        
        description = result.get("description", [""])
        if description and description[0]:
            text = description[0].split('.')[0].strip()
            return self._simplify_text(text)[:200]
        
        return "Prescription medication - consult your doctor"
    
    def _get_dosage(self, result):
        """Extract typical dosage"""
        dosage_text = result.get("dosage_and_administration", [""])
        if dosage_text and dosage_text[0]:
            text = dosage_text[0]
            dosages = re.findall(r'\d+\s*(?:mg|mcg|ml|g|units?)', text, re.IGNORECASE)
            if dosages:
                return dosages[0]
        return "As prescribed by doctor"
    
    def _get_frequency(self, result):
        """Extract how often to take"""
        dosage_text = result.get("dosage_and_administration", [""])
        if dosage_text and dosage_text[0]:
            text = dosage_text[0].lower()
            if "once daily" in text or "once a day" in text or "qd" in text:
                return "Once daily"
            elif "twice daily" in text or "bid" in text:
                return "Twice daily"
            elif "three times" in text or "tid" in text:
                return "Three times daily"
            elif "four times" in text or "qid" in text:
                return "Four times daily"
        return "As directed by your doctor"
    
    def _get_side_effects(self, result):
        """Extract common side effects"""
        adverse = result.get("adverse_reactions", [""])
        if adverse and adverse[0]:
            text = adverse[0][:300]
            effects = []
            lines = text.split('\n')
            for line in lines[:5]:
                line = line.strip('•-* \t')
                if line and 3 < len(line) < 50:
                    effects.append(line.capitalize())
            if effects:
                return effects[:5]
        return ["See package information"]
    
    def _get_warnings(self, result):
        """Extract important warnings"""
        warnings = result.get("warnings_and_cautions", [""])
        if not warnings or not warnings[0]:
            warnings = result.get("warnings", [""])
        if not warnings or not warnings[0]:
            warnings = result.get("boxed_warning", [""])
        
        if warnings and warnings[0]:
            text = warnings[0]
            first_warning = text.split('.')[0].strip()
            return self._simplify_text(first_warning)[:200]
        return "Consult your doctor before use"
    
    def _simplify_text(self, text):
        """Replace medical jargon with simpler terms"""
        replacements = {
            "indicated for": "used to treat",
            "indicated for the treatment of": "treats",
            "administered": "given",
            "administration": "taking",
            "hypertension": "high blood pressure",
            "diabetes mellitus": "diabetes",
            "hyperlipidemia": "high cholesterol",
            "dyslipidemia": "abnormal cholesterol",
            "myocardial infarction": "heart attack",
            "cerebrovascular accident": "stroke",
            "angina pectoris": "chest pain",
            "patients with": "people with",
            "patients": "people",
            "therapeutic": "treatment",
            "prophylaxis": "prevention",
            "concomitant": "together with",
            "contraindicated": "should not be used"
        }
        
        text_lower = text.lower()
        for medical, simple in replacements.items():
            text_lower = text_lower.replace(medical, simple)
        
        return text_lower.capitalize()


# Initialize API
fda_api = FDADrugAPI()