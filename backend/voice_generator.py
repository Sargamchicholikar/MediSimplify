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
Optimized Voice Generator
FREE forever with gTTS
"""

import os
from gtts import gTTS
import re

class VoiceGenerator:
    def __init__(self):
        self.output_dir = "data/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.lang_codes = {
            "English": "en",
            "Hindi": "hi",
            "Gujarati": "gu",
            "Punjabi": "pa",
            "Malayalam": "ml",
            "Bengali": "bn",
            "Assamese": "as",
            "Tamil": "ta",
            "Telugu": "te",
            "Marathi": "mr"
        }
        
        print("✅ Voice Generator ready (Optimized gTTS - FREE)")
    
    def text_to_speech(self, text, language="English"):
        """Generate optimized TTS"""
        
        try:
            print(f"🔊 Generating in {language}...")
            
            lang_code = self.lang_codes.get(language, "en")
            
            # Clean thoroughly
            clean_text = self._clean_for_speech(text)
            
            # Summarize if too long
            if len(clean_text) > 2000:
                clean_text = self._create_summary(clean_text)
            
            # Optimize for mixed language
            if language != "English":
                clean_text = self._add_pauses_for_clarity(clean_text)
            
            # Generate with optimizations
            use_slow = (language != "English")  # Slow = clearer
            
            tts = gTTS(
                text=clean_text,
                lang=lang_code,
                slow=use_slow,
                tld='co.in'
            )
            
            filename = f"audio_{language}_{abs(hash(clean_text[:50]))}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            tts.save(filepath)
            
            print(f"✅ Audio: {filename} (Slow mode: {use_slow})")
            
            return filepath
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None
    
    def _add_pauses_for_clarity(self, text):
        """Add pauses for better flow in Indian languages"""
        
        # Add pauses after sentences
        text = text.replace('. ', '... ')
        text = text.replace('। ', '... ')  # Devanagari period
        
        # Add micro-pauses after commas
        text = text.replace(', ', ',  ')
        
        return text
    
    def _clean_for_speech(self, text):
        """Remove ALL special characters"""
        
        # Remove emojis
        text = re.sub(r'[✅⚠️❌🔍💊📊🔬💡📋🏥🦴💥⏱️📅🩸🇮🇳🇬🇧📸📄🎯🚨🏃]', '', text)
        
        # Remove markdown
        text = re.sub(r'\*+(.+?)\*+', r'\1', text)
        text = re.sub(r'_+(.+?)_+', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove brackets and special chars
        text = re.sub(r'[\[\]{}()#|<>]', '', text)
        
        # Replace symbols
        text = text.replace('%', ' percent')
        text = text.replace('mg/dL', ' milligrams per deciliter')
        text = text.replace('/', ' per ')
        text = text.replace('&', ' and ')
        
        # Clean formatting
        text = re.sub(r'\n+', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _create_summary(self, text):
        """Summarize long text"""
        sentences = re.split(r'[.!?।]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        summary = '. '.join(sentences[:15])
        summary += ". For complete details, please read the full report."
        
        return summary


# Initialize
voice_generator = VoiceGenerator()