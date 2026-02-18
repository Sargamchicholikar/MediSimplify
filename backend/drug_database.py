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
Drug Combinations for Disease Detection
Only used for detecting conditions from drug patterns
"""

# Common drug combinations that indicate specific conditions
DRUG_COMBINATIONS = {
    frozenset(["metformin", "glimepiride"]): {
        "condition": "Type 2 Diabetes (Moderate to Severe)",
        "explanation": "Your blood sugar needs two medications to control it properly"
    },
    frozenset(["metformin", "glipizide"]): {
        "condition": "Type 2 Diabetes (Moderate to Severe)",
        "explanation": "Your blood sugar needs two medications to control it properly"
    },
    frozenset(["amlodipine", "telmisartan"]): {
        "condition": "High Blood Pressure (Combination Therapy)",
        "explanation": "Your blood pressure needs two medications working together"
    },
    frozenset(["amlodipine", "losartan"]): {
        "condition": "High Blood Pressure (Combination Therapy)",
        "explanation": "Your blood pressure needs two medications working together"
    },
    frozenset(["aspirin", "atorvastatin"]): {
        "condition": "Heart Disease Prevention",
        "explanation": "These medications protect your heart and blood vessels"
    },
    frozenset(["aspirin", "clopidogrel"]): {
        "condition": "Heart Disease / Stroke Prevention",
        "explanation": "Dual antiplatelet therapy to prevent blood clots"
    },
    frozenset(["metformin", "atorvastatin", "amlodipine"]): {
        "condition": "Metabolic Syndrome",
        "explanation": "You have multiple conditions: diabetes, high cholesterol, and high blood pressure"
    },
    frozenset(["levothyroxine"]): {
        "condition": "Hypothyroidism (Low Thyroid)",
        "explanation": "Your thyroid gland is not producing enough hormone"
    },
    frozenset(["insulin"]): {
        "condition": "Diabetes (Type 1 or Advanced Type 2)",
        "explanation": "Your blood sugar requires insulin treatment"
    },
}

# Medical abbreviations (still useful)
ABBREVIATIONS = {
    "OD": "Once Daily",
    "BD": "Twice Daily",
    "BID": "Twice Daily",
    "TID": "Three Times Daily",
    "QID": "Four Times Daily",
    "PRN": "As Needed",
    "AC": "Before Meals",
    "PC": "After Meals",
    "HS": "At Bedtime",
    "STAT": "Immediately",
    "SOS": "If Necessary",
    "QH": "Every Hour",
    "Q4H": "Every 4 Hours",
    "Q6H": "Every 6 Hours",
    "Q8H": "Every 8 Hours",
    "Q12H": "Every 12 Hours",
    "TDS": "Three Times Daily",
}