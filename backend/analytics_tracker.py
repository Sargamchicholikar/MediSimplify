"""
Analytics Tracker - Privacy-Preserving Usage Tracking
Tracks anonymous usage metrics for portfolio metrics

Copyright (c) 2026 Sargam Chicholikar
Created: February 2026
"""

import os
import json
from datetime import datetime
from collections import defaultdict

class AnalyticsTracker:
    def __init__(self):
        """Initialize analytics tracker"""
        
        self.analytics_dir = "analytics"
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        self.stats_file = os.path.join(self.analytics_dir, "usage_stats.json")
        self._initialize_stats()
        
        print("✅ Analytics Tracker ready (Privacy-preserving)")
    
    def _initialize_stats(self):
        """Initialize or load statistics"""
        if not os.path.exists(self.stats_file):
            stats = {
                "total_analyses": 0,
                "prescriptions_analyzed": 0,
                "labs_analyzed": 0,
                "xrays_analyzed": 0,
                "manual_drug_entries": 0,
                "languages": {},
                "daily_stats": {},
                "hourly_patterns": {},
                "feature_usage": {
                    "voice_playback": 0,
                    "multi_report_analysis": 0
                },
                "started_tracking": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
    
    def track_prescription_analysis(self, language="English", is_upload=True):
        """Track prescription analysis"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            stats["total_analyses"] += 1
            
            if is_upload:
                stats["prescriptions_analyzed"] += 1
            else:
                stats["manual_drug_entries"] += 1
            
            self._update_common_stats(stats, language)
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            print(f"📊 Tracked: Prescription ({language})")
            
        except Exception as e:
            print(f"⚠️ Analytics error: {e}")
    
    def track_lab_analysis(self, language="English"):
        """Track lab report analysis"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            stats["total_analyses"] += 1
            stats["labs_analyzed"] += 1
            
            self._update_common_stats(stats, language)
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            print(f"📊 Tracked: Lab Report ({language})")
            
        except Exception as e:
            print(f"⚠️ Analytics error: {e}")
    
    def track_xray_analysis(self, language="English"):
        """Track X-ray analysis"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            stats["total_analyses"] += 1
            stats["xrays_analyzed"] += 1
            
            self._update_common_stats(stats, language)
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            print(f"📊 Tracked: X-Ray ({language})")
            
        except Exception as e:
            print(f"⚠️ Analytics error: {e}")
    
    def track_voice_usage(self, report_type, language="English"):
        """Track when voice feature is used"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            stats["feature_usage"]["voice_playback"] += 1
            stats["last_updated"] = datetime.now().isoformat()
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            print(f"🔊 Tracked: Voice ({report_type}, {language})")
            
        except Exception as e:
            print(f"⚠️ Voice tracking error: {e}")
    
    def track_multi_report(self):
        """Track when user uploads multiple report types at once"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
            
            stats["feature_usage"]["multi_report_analysis"] += 1
            stats["last_updated"] = datetime.now().isoformat()
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            print(f"📊 Tracked: Multi-report analysis")
            
        except Exception as e:
            print(f"⚠️ Tracking error: {e}")
    
    def _update_common_stats(self, stats, language):
        """Update language, daily, and hourly stats"""
        
        # Language tracking
        if language not in stats["languages"]:
            stats["languages"][language] = 0
        stats["languages"][language] += 1
        
        # Daily tracking
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in stats["daily_stats"]:
            stats["daily_stats"][today] = 0
        stats["daily_stats"][today] += 1
        
        # Hourly patterns (for usage analysis)
        hour = datetime.now().strftime("%H:00")
        if hour not in stats["hourly_patterns"]:
            stats["hourly_patterns"][hour] = 0
        stats["hourly_patterns"][hour] += 1
        
        # Update timestamp
        stats["last_updated"] = datetime.now().isoformat()
    
    def get_statistics(self):
        """Get all statistics"""
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "total_analyses": 0,
                "prescriptions_analyzed": 0,
                "labs_analyzed": 0,
                "xrays_analyzed": 0
            }
    
    def generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        stats = self.get_statistics()
        
        report = f"""
{'='*70}
MediSimplify - Usage Analytics Report
{'='*70}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

OVERALL USAGE:
-------------
Total Analyses:          {stats.get('total_analyses', 0)}
  - Prescriptions:       {stats.get('prescriptions_analyzed', 0)}
  - Lab Reports:         {stats.get('labs_analyzed', 0)}
  - X-Rays:              {stats.get('xrays_analyzed', 0)}
  - Manual Drug Entry:   {stats.get('manual_drug_entries', 0)}

LANGUAGE PREFERENCES:
--------------------
"""
        
        languages = stats.get('languages', {})
        total_lang = sum(languages.values()) or 1
        
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_lang) * 100
            report += f"{lang:15} : {count:4} ({percentage:5.1f}%)\n"
        
        report += f"""
FEATURE USAGE:
-------------
Voice Playback Used:     {stats['feature_usage'].get('voice_playback', 0)} times
Multi-Report Analysis:   {stats['feature_usage'].get('multi_report_analysis', 0)} times

USAGE PATTERNS:
--------------
Peak Usage Hours (Top 5):
"""
        
        hourly = stats.get('hourly_patterns', {})
        if hourly:
            sorted_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:5]
            for hour, count in sorted_hours:
                report += f"  {hour:8} : {count:3} analyses\n"
        
        report += f"""
Daily Activity (Last 7 Days):
"""
        daily = stats.get('daily_stats', {})
        if daily:
            sorted_days = sorted(daily.items(), reverse=True)[:7]
            for day, count in sorted_days:
                report += f"  {day:12} : {count:3} analyses\n"
        
        report += f"""
TRACKING PERIOD:
---------------
Started:      {stats.get('started_tracking', 'Unknown')}
Last Updated: {stats.get('last_updated', 'Unknown')}

{'='*70}
Impact: Serving medical information in {len(languages)} languages
{'='*70}
"""
        
        # Save report
        report_path = os.path.join(self.analytics_dir, "ANALYTICS_REPORT.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        return report


# Initialize
analytics_tracker = AnalyticsTracker()