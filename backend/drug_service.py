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
FDA-Only Drug Service
No local database - everything from FDA API
"""

import json
import os
from datetime import datetime

try:
    from drug_api import fda_api
    FDA_API_AVAILABLE = True
except ImportError:
    FDA_API_AVAILABLE = False
    print("⚠️ FDA API not available")

class FDAOnlyDrugService:
    def __init__(self):
        self.cache_file = "data/drug_cache.json"
        self.cache = self._load_cache()
        self.session_cache = {}
        
        if not FDA_API_AVAILABLE:
            raise Exception("FDA API is required! Install 'requests' package.")
        
        print("✅ FDA-Only Drug Service initialized")
    
    def _load_cache(self):
        """Load previously fetched drugs from cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    print(f"📦 Loaded {len(cache)} drugs from cache")
                    return cache
            except Exception as e:
                print(f"⚠️ Could not load cache: {e}")
                return {}
        return {}
    
    def get_drug_info(self, drug_name):
        """
        Get drug info with smart caching:
        1. Check session cache (this runtime)
        2. Check file cache (previous runs)
        3. Query FDA API
        4. Save to cache
        """
        drug_lower = drug_name.lower().strip()
        
        # Tier 1: Session cache (instant)
        if drug_lower in self.session_cache:
            print(f"⚡ From session cache: {drug_name}")
            return self.session_cache[drug_lower]
        
        # Tier 2: File cache (very fast)
        if drug_lower in self.cache:
            print(f"📦 From file cache: {drug_name}")
            self.session_cache[drug_lower] = self.cache[drug_lower]
            return self.cache[drug_lower]
        
        # Tier 3: FDA API (requires internet)
        print(f"🌐 Querying FDA API for: {drug_name}")
        fda_result = fda_api.search_drug(drug_name)
        
        if fda_result:
            # Cache it
            self.session_cache[drug_lower] = fda_result
            self._save_to_cache(drug_lower, fda_result)
            return fda_result
        
        # Not found
        print(f"❌ Not found: {drug_name}")
        return {
            "name": drug_name.title(),
            "category": "Unknown",
            "treats": "Drug not found",
            "simple_explanation": "Information not available. Please consult your doctor.",
            "common_dosage": "N/A",
            "frequency": "N/A",
            "side_effects": ["Information not available"],
            "warnings": "Consult your doctor",
            "source": "Not Found",
            "confidence": "none"
        }
    
    def _save_to_cache(self, drug_name, drug_info):
        """Save to persistent cache"""
        try:
            # Add metadata
            drug_info["cached_at"] = datetime.now().isoformat()
            
            # Update cache
            self.cache[drug_name] = drug_info
            
            # Save to file
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Cached: {drug_name}")
            
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
    
    def get_stats(self):
        """Get statistics"""
        return {
            "cached_drugs": len(self.cache),
            "session_cache": len(self.session_cache),
            "fda_api_enabled": FDA_API_AVAILABLE
        }
    
    def clear_cache(self):
        """Clear cache (admin function)"""
        self.cache = {}
        self.session_cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("🗑️ Cache cleared")


# Initialize service
drug_service = FDAOnlyDrugService()