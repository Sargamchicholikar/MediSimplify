"""
User Feedback Collector
Collects user feedback for product improvement

Copyright (c) 2026 Sargam Chicholikar
Created: February 2026
"""

import os
import json
from datetime import datetime

class FeedbackCollector:
    def __init__(self):
        """Initialize feedback collector"""
        
        self.feedback_dir = "user_feedback"
        os.makedirs(self.feedback_dir, exist_ok=True)
        
        self.feedback_file = os.path.join(self.feedback_dir, "all_feedback.json")
        
        # Initialize if not exists
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w') as f:
                json.dump([], f)
        
        print("✅ Feedback Collector ready")
    
    def save_feedback(self, feedback_data):
        """
        Save user feedback
        
        Args:
            feedback_data: {
                'rating': 1-5,
                'comments': str,
                'feature_used': 'prescription/lab/xray',
                'language': str,
                'email': str (optional),
                'feedback_type': 'general/bug/feature_request'
            }
        """
        try:
            # Load existing feedback
            with open(self.feedback_file, 'r') as f:
                all_feedback = json.load(f)
            
            # Add metadata
            feedback_entry = {
                'id': f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'rating': feedback_data.get('rating', 0),
                'comments': feedback_data.get('comments', ''),
                'feature_used': feedback_data.get('feature_used', 'unknown'),
                'language': feedback_data.get('language', 'English'),
                'email': feedback_data.get('email', 'anonymous'),
                'feedback_type': feedback_data.get('feedback_type', 'general')
            }
            
            # Append
            all_feedback.append(feedback_entry)
            
            # Save
            with open(self.feedback_file, 'w') as f:
                json.dump(all_feedback, f, indent=2)
            
            # Also save individual text file (human-readable)
            self._save_individual_feedback(feedback_entry)
            
            print(f"💬 Feedback saved: {feedback_entry['id']} (Rating: {feedback_entry['rating']}/5)")
            
            return feedback_entry['id']
            
        except Exception as e:
            print(f"⚠️ Feedback save error: {e}")
            return None
    
    def _save_individual_feedback(self, feedback_entry):
        """Save individual feedback as text file"""
        
        feedback_text = f"""User Feedback Report
{'='*60}

ID: {feedback_entry['id']}
Date: {feedback_entry['timestamp']}
Rating: {'⭐' * feedback_entry['rating']} ({feedback_entry['rating']}/5)

Feature Used: {feedback_entry['feature_used']}
Language: {feedback_entry['language']}
Type: {feedback_entry['feedback_type']}

Comments:
{'-'*60}
{feedback_entry['comments']}
{'-'*60}

Contact: {feedback_entry['email']}

{'='*60}
"""
        
        filepath = os.path.join(self.feedback_dir, f"{feedback_entry['id']}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(feedback_text)
    
    def get_all_feedback(self):
        """Get all feedback"""
        try:
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_statistics(self):
        """Get feedback statistics"""
        try:
            with open(self.feedback_file, 'r') as f:
                all_feedback = json.load(f)
            
            if not all_feedback:
                return {
                    'total_feedback': 0,
                    'average_rating': 0,
                    'rating_distribution': {}
                }
            
            total = len(all_feedback)
            ratings = [f['rating'] for f in all_feedback if f['rating'] > 0]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Rating distribution
            rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for r in ratings:
                rating_dist[r] = rating_dist.get(r, 0) + 1
            
            # Feature usage
            features = {}
            for f in all_feedback:
                feat = f.get('feature_used', 'unknown')
                features[feat] = features.get(feat, 0) + 1
            
            return {
                'total_feedback': total,
                'average_rating': round(avg_rating, 2),
                'rating_distribution': rating_dist,
                'feature_feedback': features
            }
            
        except Exception as e:
            print(f"⚠️ Stats error: {e}")
            return {}


# Initialize
feedback_collector = FeedbackCollector()