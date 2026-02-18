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
Drug Information Translator
Translates FDA drug info to Indian languages
"""

import requests
import os

class DrugTranslator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        
        self.available = bool(self.api_key)
        
        if self.available:
            print("✅ Drug Translator ready")
    
    def translate_drug_info(self, drug_info, target_language):
        """Translate drug information to target language"""
        
        if not self.available or target_language == "English":
            return drug_info
        
        try:
            print(f"🌐 Translating {drug_info['name']} to {target_language}...")
            
            prompt = f"""Translate this medication information to simple, everyday {target_language}.

Drug Name: {drug_info['name']}
Treats: {drug_info['treats']}
What it does: {drug_info['explanation']}
Dosage: {drug_info['dosage']}
When to take: {drug_info['frequency']}
Warning: {drug_info['warnings']}

Translate to natural {target_language} that common people speak. You can mix English for medical terms.

Format:
NAME: [keep in English]
TREATS: [translated]
WHAT IT DOES: [translated in simple {target_language}]
DOSAGE: [keep English + add {target_language} if helpful]
WHEN: [translated]
WARNING: [translated in simple {target_language}]"""

            response = requests.post(
                self.groq_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You translate medical information to simple, everyday {target_language}. Use words common people use."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.4,
                    "max_tokens": 600
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data['choices'][0]['message']['content']
                
                # Parse translated response
                translated = {
                    "name": drug_info['name'],  # Keep drug name in English
                    "treats": self._extract_field(translated_text, "TREATS") or drug_info['treats'],
                    "explanation": self._extract_field(translated_text, "WHAT IT DOES") or drug_info['explanation'],
                    "dosage": self._extract_field(translated_text, "DOSAGE") or drug_info['dosage'],
                    "frequency": self._extract_field(translated_text, "WHEN") or drug_info['frequency'],
                    "warnings": self._extract_field(translated_text, "WARNING") or drug_info['warnings'],
                    "language": target_language
                }
                
                print(f"✅ Translated {drug_info['name']}")
                
                return translated
            else:
                return drug_info
                
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return drug_info
    
    def translate_multiple_drugs(self, drugs_list, target_language):
        """Translate multiple drugs"""
        
        if not self.available or target_language == "English":
            return drugs_list
        
        print(f"🌐 Translating {len(drugs_list)} drugs to {target_language}...")
        
        translated_drugs = []
        
        for drug in drugs_list:
            translated = self.translate_drug_info(drug, target_language)
            translated_drugs.append(translated)
        
        return translated_drugs
    
    def _extract_field(self, text, field_name):
        """Extract field from translated text"""
        try:
            import re
            pattern = f"{field_name}:?\\s*(.+?)(?=NAME:|TREATS:|WHAT IT DOES:|DOSAGE:|WHEN:|WARNING:|$)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                content = content.replace('\n', ' ')
                content = ' '.join(content.split())
                return content
            
            return ""
        except:
            return ""


# Initialize
drug_translator = DrugTranslator()