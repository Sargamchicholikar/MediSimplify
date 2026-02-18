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
Advanced X-Ray Vision Analysis using Gemini 2.5
Detects fractures, identifies bones, predicts recovery
"""

import google.generativeai as genai
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv() 

class AdvancedXRayVisionAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        
        if api_key:
            genai.configure(api_key=api_key)
            
            try:
                # Use latest Gemini 2.5 Flash model
                self.model = genai.GenerativeModel('models/gemini-2.5-flash')
                
                # Quick test to verify it works
                test_response = self.model.generate_content("Test")
                
                self.available = True
                print("✅ X-Ray Vision Analyzer ready (Gemini 2.5 Flash)")
                
            except Exception as e:
                print(f"⚠️ Gemini initialization error: {e}")
                self.available = False
        else:
            self.available = False
            print("⚠️ Gemini API key not set")
    
    def analyze_xray_detailed(self, image_bytes, language="English"):
        """
        Detailed X-ray image analysis with fracture detection
        """
        if not self.available:
            return self._fallback_analysis(language)
        
        try:
            print(f"🔬 Vision AI analyzing X-ray image...")
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Get language instruction
            lang_inst = self._get_language_instruction(language)
            
            # Comprehensive analysis prompt
            prompt = f"""You are an expert radiologist analyzing an X-ray image. {lang_inst}

Look at this X-ray carefully and provide detailed analysis:

BODY PART: [Identify which bone or body part this is. Be specific - e.g., "Right Wrist (Distal Radius)", "Left Ankle", "Chest"]

FRACTURE: [Is there a fracture/broken bone? Answer clearly: YES or NO]

If FRACTURE = YES, provide these details:
  TYPE: [Classify the fracture type:
    - Hairline fracture (small crack)
    - Simple fracture (clean break, aligned)
    - Displaced fracture (bone pieces separated)
    - Comminuted fracture (multiple fragments)
    - Compound fracture (bone through skin)
  ]
  LOCATION: [Exactly where on the bone is the fracture? Be precise]
  CAUSE: [Based on fracture pattern, what likely caused this?
    - Fall on outstretched hand
    - Twisting/rolling injury
    - Direct impact/blow
    - Sports injury
    - Motor accident
    - Stress/overuse
  ]
  RECOVERY: [Estimate healing time based on:
    - Bone type and location
    - Fracture severity
    - Assume adult patient
    Give specific timeframe like "4-6 weeks", "8-12 weeks"
  ]

FINDINGS: [List 4-6 key observations, each on new line with emoji:
✅ [Normal findings - things that look good]
⚠️ [Things to monitor - borderline findings]
❌ [Problems detected]
]

EXPLANATION: [Explain what you see in 2-3 simple sentences. Use everyday language, not medical jargon. Help patient understand their injury.]

ACTION: [Specific, practical next steps for the patient. If fracture: urgency level, treatment needed, care instructions]

IMPORTANT: Be accurate, honest, and helpful. Use simple words anyone can understand."""

            # Call Gemini Vision API
            response = self.model.generate_content([prompt, image])
            
            explanation = response.text
            
            print(f"✅ Vision analysis complete")
            print(f"AI Response ({len(explanation)} chars):")
            print(f"{explanation[:300]}...")
            
            # Parse the structured response
            parsed = self._parse_response(explanation, language)
            
            return parsed
            
        except Exception as e:
            print(f"⚠️ Analysis Error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_analysis(language)
    
    def _parse_response(self, ai_text, language):
        """Parse AI response into structured format"""
        import re
        
        def extract(field):
            # Pattern to extract each field
            pattern = f"{field}:?\\s*(.+?)(?=BODY PART:|FRACTURE:|TYPE:|LOCATION:|CAUSE:|RECOVERY:|FINDINGS:|EXPLANATION:|ACTION:|$)"
            match = re.search(pattern, ai_text, re.IGNORECASE | re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                
                # Keep formatting for multi-line fields
                if field in ["FINDINGS", "EXPLANATION", "ACTION"]:
                    return content
                else:
                    # Single line fields - clean up
                    return content.replace('\n', ' ').strip()
            
            return ""
        
        # Extract all fields
        body_part = extract("BODY PART")
        fracture_status = extract("FRACTURE")
        frac_type = extract("TYPE")
        location = extract("LOCATION")
        cause = extract("CAUSE")
        recovery = extract("RECOVERY")
        findings = extract("FINDINGS")
        explanation = extract("EXPLANATION")
        action = extract("ACTION")
        
        # Determine if fracture present
        has_fracture = "yes" in fracture_status.lower() and "no" not in fracture_status.lower()
        
        # Determine status color
        if has_fracture:
            # Red for fracture
            color = "red"
        else:
            # Check if there are any warnings in findings
            if "⚠️" in findings or "❌" in findings:
                color = "orange"
            else:
                color = "green"
        
        return {
            "xray_type": f"X-Ray: {body_part}" if body_part else "X-Ray Analysis",
            "body_part": body_part or "Not specified",
            "has_fracture": has_fracture,
            "fracture_type": frac_type if has_fracture else "No fracture detected",
            "fracture_location": location if has_fracture else "N/A",
            "likely_cause": cause if has_fracture else "N/A",
            "recovery_time": recovery if has_fracture else "N/A",
            "findings": findings or "Analysis completed",
            "overall_result": explanation or "Please see your doctor for detailed interpretation",
            "action": action or "Consult your doctor with this X-ray",
            "color": color,
            "language": language,
            "source": "Gemini 2.5 Vision AI"
        }
    
    def _get_language_instruction(self, language):
        """Get language-specific instructions"""
        
        instructions = {
            "English": "Use simple, everyday English. Avoid medical jargon.",
            
            "Hindi": """Use simple Hindi (हिन्दी). You can mix Hindi and English (Hinglish) for medical terms.
Example: "आपकी हड्डी टूटी हुई है (bone is broken)। यह ankle में fracture है।"
Use Devanagari script for Hindi words.""",
            
            "Gujarati": """Use simple Gujarati (ગુજરાતી). Mix Gujarati-English for medical terms.
Example: "તમારું હાડકું તૂટેલું છે (bone is broken)। આ ankle fracture છે।"
Use Gujarati script.""",
            
            "Punjabi": """Use simple Punjabi (ਪੰਜਾਬੀ). Mix Punjabi-English for medical terms.
Use Gurmukhi script.""",
            
            "Malayalam": """Use simple Malayalam (മലയാളം). Mix Malayalam-English for medical terms.
Use Malayalam script.""",
            
            "Bengali": """Use simple Bengali (বাংলা). Mix Bengali-English for medical terms.
Use Bengali script.""",
            
            "Assamese": """Use simple Assamese (অসমীয়া). Mix Assamese-English for medical terms.
Use Bengali script.""",
            
            "Marathi": """Use simple Marathi (मराठी). Mix Marathi-English for medical terms.
Use Devanagari script.""",
            
            "Tamil": """Use simple Tamil (தமிழ்). Mix Tamil-English for medical terms.
Use Tamil script.""",
            
            "Telugu": """Use simple Telugu (తెలుగు). Mix Telugu-English for medical terms.
Use Telugu script."""
        }
        
        return instructions.get(language, instructions["English"])
    
    def _fallback_analysis(self, language):
        """Fallback when API not available"""
        
        fallback_messages = {
            "English": {
                "findings": "Unable to analyze. API not available.",
                "result": "Please consult a radiologist for proper X-ray interpretation.",
                "action": "Show this X-ray to your doctor"
            },
            "Hindi": {
                "findings": "विश्लेषण नहीं हो सका। API उपलब्ध नहीं है।",
                "result": "कृपया रेडियोलॉजिस्ट से X-ray की व्याख्या करवाएं।",
                "action": "यह X-ray अपने डॉक्टर को दिखाएं"
            },
            "Gujarati": {
                "findings": "વિશ્લેષણ નહીં થઈ શક્યું। API ઉપલબ્ધ નથી।",
                "result": "કૃપા કરીને રેડિયોલોજિસ્ટ પાસે X-ray ચકાસો।",
                "action": "આ X-ray તમારા ડૉક્ટરને બતાવો"
            }
        }
        
        msgs = fallback_messages.get(language, fallback_messages["English"])
        
        return {
            "xray_type": "X-Ray Image",
            "body_part": "Unknown",
            "has_fracture": False,
            "fracture_type": "N/A",
            "fracture_location": "N/A",
            "likely_cause": "N/A",
            "recovery_time": "N/A",
            "findings": msgs["findings"],
            "overall_result": msgs["result"],
            "action": msgs["action"],
            "color": "blue",
            "language": language,
            "source": "Fallback"
        }


# Initialize
advanced_xray_analyzer = AdvancedXRayVisionAnalyzer()