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
AI Lab Analyzer with Multi-Language Support
Supports: English, Hindi, Gujarati (expandable)
"""

import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

class GroqLabAnalyzer:
    def __init__(self):
        """Initialize Groq analyzer"""
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        
        self.groq_available = bool(self.api_key)
        
        # Supported languages
        self.supported_languages = {
            "English": "English",
            "Hindi": "हिन्दी",
            "Gujarati": "ગુજરાતી",
            "Marathi": "मराठी",
            "Tamil": "தமிழ்",
            "Telugu": "తెలుగు"
        }
        
        if self.groq_available:
            print(f"✅ Groq AI Lab Analyzer ready (Multi-language support!)")
        else:
            print("⚠️ Groq API key not found")
    
    def analyze_lab_result(self, test_name, value, unit="", language="English"):
        """Analyze single lab test in specified language"""
        
        if not self.groq_available:
            return self._fallback_analysis(test_name, value, unit)
        
        try:
            print(f"🤖 Analyzing: {test_name} = {value} {unit} (Language: {language})")
            
            # Language-specific instructions
            lang_instructions = self._get_language_instructions(language)
            
            prompt = f"""You're explaining a medical test to a patient. {lang_instructions}

Test: {test_name}
Value: {value} {unit}

Explain warmly and simply:

WHAT IS IT: [Simple explanation with everyday analogy]
STATUS: [{self._get_status_labels(language)}]
MEANING: [What this value means - 2 sentences max, simple words]
ACTION: [One practical action]

Be clear, kind, and helpful."""

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
                            "content": lang_instructions
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.4,
                    "max_tokens": 500
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_text = data['choices'][0]['message']['content']
                
                parsed = self._parse_ai_response(ai_text, test_name, value, unit)
                parsed['language'] = language
                return parsed
            else:
                return self._fallback_analysis(test_name, value, unit)
                
        except Exception as e:
            print(f"⚠️ Exception: {e}")
            return self._fallback_analysis(test_name, value, unit)
    
    def analyze_full_report_text(self, extracted_text, language="English"):
        """
        Analyze entire lab report in specified language
        """
        if not self.groq_available:
            return []
        
        try:
            print(f"🤖 AI analyzing complete report in {language} ({len(extracted_text)} chars)")
            
            text_sample = extracted_text[:3000]
            
            # Language-specific instructions
            lang_instructions = self._get_language_instructions(language)
            status_labels = self._get_status_labels(language)
            
            prompt = f"""You're a health educator explaining lab tests. {lang_instructions}

Lab Report:
{text_sample}

For EACH test found, explain like this:

---
TEST: [Test name in simple terms]
VALUE: [Patient's value with unit]
STATUS: [{status_labels}]
MEANING: [Explain in simple everyday words - MAX 2 sentences. Use analogies people understand]
ACTION: [ONE simple action]
---

CRITICAL RULES:
1. Use words a 10-year-old understands
2. NO medical jargon - use everyday language
3. Use analogies: "like car fuel level", "like blood flow in pipes"
4. Keep VERY brief - 2 sentences max per section
5. Be warm and helpful

Extract ALL tests from the report!"""

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
                            "content": lang_instructions
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5,
                    "max_tokens": 4000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_text = data['choices'][0]['message']['content']
                
                print(f"✅ AI response received ({len(ai_text)} chars)")
                
                tests = self._parse_multiple_tests_simple(ai_text)
                
                # Add language tag
                for test in tests:
                    test['language'] = language
                
                print(f"✅ Extracted {len(tests)} tests in {language}")
                
                return tests
            else:
                print(f"⚠️ AI Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return []
    
    def _get_language_instructions(self, language):
        """Get language-specific instructions for AI"""
        
        instructions = {
            "English": "Use simple, everyday English. Avoid medical jargon completely.",
            
            "Hindi": """Use simple, everyday HINDI language. You can mix Hindi-English (Hinglish) for medical terms if needed.
Example: "आपका हीमोग्लोबिन कम है (Your hemoglobin is low). यह oxygen carry करता है blood में।"
Use Devanagari script for Hindi words.""",
            
            "Gujarati": """Use simple, everyday GUJARATI language. You can mix Gujarati-English for medical terms.
Use Gujarati script. Explain like you're talking to someone from Gujarat.""",
            
            "Marathi": """Use simple, everyday MARATHI language. Mix Marathi-English if needed.
Use Devanagari script for Marathi words.""",
            
            "Tamil": "Use simple, everyday TAMIL language. Use Tamil script. Explain warmly.",
            
            "Telugu": "Use simple, everyday TELUGU language. Use Telugu script. Be clear and helpful."
        }
        
        return instructions.get(language, instructions["English"])
    
    def _get_status_labels(self, language):
        """Get status labels in specified language"""
        
        labels = {
            "English": "✅ Good / ⚠️ Warning / ❌ Needs Attention",
            "Hindi": "✅ अच्छा (Good) / ⚠️ सावधान (Careful) / ❌ ध्यान दें (Attention)",
            "Gujarati": "✅ સારું (Good) / ⚠️ સાવધાન (Careful) / ❌ ધ્યાન આપો (Attention)",
            "Marathi": "✅ चांगले (Good) / ⚠️ सावधान (Careful) / ❌ लक्ष द्या (Attention)",
            "Tamil": "✅ நல்லது (Good) / ⚠️ எச்சரிக்கை (Warning) / ❌ கவனம் (Attention)",
            "Telugu": "✅ మంచిది (Good) / ⚠️ హెచ్చరిక (Warning) / ❌ శ్రద్ధ (Attention)"
        }
        
        return labels.get(language, labels["English"])
    
    def _parse_multiple_tests_simple(self, ai_text):
        """Parse tests from AI response"""
        tests = []
        
        sections = ai_text.split('---')
        
        print(f"📋 Parsing {len(sections)} sections")
        
        for section in sections:
            section = section.strip()
            
            if len(section) < 20:
                continue
            
            test_name = self._extract_field(section, "TEST")
            value = self._extract_field(section, "VALUE")
            status = self._extract_field(section, "STATUS")
            meaning = self._extract_field(section, "MEANING")
            action = self._extract_field(section, "ACTION")
            
            if test_name and value:
                status_lower = status.lower()
                color = "green" if "✅" in status or "good" in status_lower or "अच्छा" in status or "સારું" in status else \
                       "orange" if "⚠️" in status or "warning" in status_lower or "सावधान" in status or "સાવધાન" in status else \
                       "red" if "❌" in status or "attention" in status_lower or "ध्यान" in status or "ધ્યાન" in status else \
                       "blue"
                
                tests.append({
                    "test": test_name,
                    "value": value,
                    "status": status,
                    "what_is_it": test_name,
                    "explanation": meaning or "Ask your doctor",
                    "action": action or "See doctor",
                    "color": color
                })
                
                print(f"  ✅ {test_name}: {value}")
        
        return tests
    
    def _extract_field(self, text, field_name):
        """Extract field"""
        try:
            pattern = f"{field_name}:?\\s*(.+?)(?=TEST:|VALUE:|STATUS:|MEANING:|ACTION:|WHAT IS IT:|WHAT TO DO:|$)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                content = content.replace('\n', ' ')
                content = ' '.join(content.split())
                return content
            
            return ""
        except:
            return ""
    
    def _parse_ai_response(self, ai_text, test_name, value, unit):
        """Parse single test"""
        
        what_is_it = self._extract_section(ai_text, "WHAT IS IT")
        status = self._extract_section(ai_text, "STATUS")
        meaning = self._extract_section(ai_text, "MEANING")
        action = self._extract_section(ai_text, "ACTION")
        
        color = "blue"
        if "✅" in status or "good" in status.lower() or "अच्छा" in status:
            color = "green"
        elif "⚠️" in status or "warning" in status.lower() or "सावधान" in status:
            color = "orange"
        elif "❌" in status or "attention" in status.lower() or "ध्यान" in status:
            color = "red"
        
        return {
            "test": test_name,
            "value": f"{value} {unit}".strip(),
            "status": status,
            "what_is_it": what_is_it,
            "explanation": meaning,
            "action": action,
            "color": color
        }
    
    def _extract_section(self, text, section_name):
        """Extract section"""
        try:
            pattern = f"{section_name}:?\\s*(.+?)(?=WHAT IS IT:|STATUS:|MEANING:|ACTION:|$)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                content = ' '.join(content.split())
                return content
            
            return ""
        except:
            return ""
    
    def _fallback_analysis(self, test_name, value, unit):
        """Fallback"""
        return {
            "test": test_name,
            "value": f"{value} {unit}".strip(),
            "status": "Recorded",
            "what_is_it": f"{test_name}",
            "explanation": "Please ask your doctor about this result.",
            "action": "Discuss with doctor",
            "color": "blue"
        }
    
    def analyze_full_report(self, test_results, language="English"):
        """Analyze list of tests in specified language"""
        analyses = []
        
        print(f"\n🧪 Analyzing {len(test_results)} tests in {language}...")
        
        for test in test_results:
            analysis = self.analyze_lab_result(
                test.get("test_name", "Unknown"),
                test.get("value", 0),
                test.get("unit", ""),
                language=language
            )
            analyses.append(analysis)
        
        print(f"✅ Completed\n")
        return analyses


# Initialize
ai_lab_analyzer = GroqLabAnalyzer()