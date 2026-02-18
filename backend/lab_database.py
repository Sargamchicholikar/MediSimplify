"""
Common lab tests with reference ranges
"""

LAB_TESTS = {
    # Diabetes tests
    "HbA1c": {
        "full_name": "Glycated Hemoglobin",
        "category": "Diabetes",
        "unit": "%",
        "ranges": {
            "normal": (0, 5.6),
            "prediabetes": (5.7, 6.4),
            "diabetes": (6.5, 15)
        },
        "explanation": {
            "normal": "Your average blood sugar over 3 months is normal. No diabetes detected.",
            "prediabetes": "Your blood sugar is higher than normal but not yet diabetes. Lifestyle changes needed urgently.",
            "diabetes": "You have diabetes. Your blood sugar has been high for the past 3 months. Treatment required."
        },
        "what_is_it": "Shows your average blood sugar level over the past 2-3 months"
    },
    
    "Fasting Blood Sugar": {
        "full_name": "Fasting Plasma Glucose",
        "category": "Diabetes",
        "unit": "mg/dL",
        "ranges": {
            "normal": (70, 99),
            "prediabetes": (100, 125),
            "diabetes": (126, 500)
        },
        "explanation": {
            "normal": "Your blood sugar after fasting overnight is normal.",
            "prediabetes": "Your fasting blood sugar is elevated. High risk of developing diabetes.",
            "diabetes": "Your fasting blood sugar indicates diabetes."
        },
        "what_is_it": "Measures blood sugar after not eating for at least 8 hours"
    },
    
    # Lipid profile
    "Total Cholesterol": {
        "full_name": "Total Cholesterol",
        "category": "Heart Health",
        "unit": "mg/dL",
        "ranges": {
            "desirable": (0, 200),
            "borderline": (200, 239),
            "high": (240, 500)
        },
        "explanation": {
            "desirable": "Your cholesterol level is healthy.",
            "borderline": "Your cholesterol is borderline high. Diet and exercise changes recommended.",
            "high": "Your cholesterol is high. Increases risk of heart disease. Medication may be needed."
        },
        "what_is_it": "Measures total amount of cholesterol (fat) in your blood"
    },
    
    "LDL": {
        "full_name": "LDL Cholesterol (Bad Cholesterol)",
        "category": "Heart Health",
        "unit": "mg/dL",
        "ranges": {
            "optimal": (0, 100),
            "near_optimal": (100, 129),
            "borderline": (130, 159),
            "high": (160, 500)
        },
        "explanation": {
            "optimal": "Your bad cholesterol is at optimal level.",
            "near_optimal": "Your bad cholesterol is acceptable but could be better.",
            "borderline": "Your bad cholesterol is borderline high. Diet changes recommended.",
            "high": "Your bad cholesterol is high. This can block arteries. Treatment needed."
        },
        "what_is_it": "Bad cholesterol that can clog arteries and cause heart attacks"
    },
    
    "HDL": {
        "full_name": "HDL Cholesterol (Good Cholesterol)",
        "category": "Heart Health",
        "unit": "mg/dL",
        "ranges": {
            "low": (0, 40),
            "acceptable": (40, 59),
            "high": (60, 200)
        },
        "explanation": {
            "low": "Your good cholesterol is too low. This increases heart disease risk. Exercise helps increase it.",
            "acceptable": "Your good cholesterol is acceptable.",
            "high": "Excellent! High good cholesterol protects against heart disease."
        },
        "what_is_it": "Good cholesterol that removes bad cholesterol from arteries"
    },
    
    "Triglycerides": {
        "full_name": "Triglycerides",
        "category": "Heart Health",
        "unit": "mg/dL",
        "ranges": {
            "normal": (0, 150),
            "borderline": (150, 199),
            "high": (200, 499),
            "very_high": (500, 2000)
        },
        "explanation": {
            "normal": "Your triglyceride level is normal.",
            "borderline": "Your triglycerides are borderline high. Reduce sugar and alcohol intake.",
            "high": "Your triglycerides are high. Increases risk of heart disease and pancreatitis.",
            "very_high": "Your triglycerides are very high. Immediate treatment required."
        },
        "what_is_it": "Type of fat in blood that stores excess energy from food"
    },
    
    # Kidney function
    "Creatinine": {
        "full_name": "Serum Creatinine",
        "category": "Kidney Function",
        "unit": "mg/dL",
        "ranges": {
            "normal_male": (0.7, 1.3),
            "normal_female": (0.6, 1.1),
            "elevated": (1.4, 10)
        },
        "explanation": {
            "normal_male": "Your kidney function is normal.",
            "normal_female": "Your kidney function is normal.",
            "elevated": "Your creatinine is elevated. Your kidneys may not be working properly."
        },
        "what_is_it": "Waste product filtered by kidneys. High levels indicate kidney problems"
    },
    
    # Liver function
    "SGPT": {
        "full_name": "ALT (Liver Enzyme)",
        "category": "Liver Function",
        "unit": "U/L",
        "ranges": {
            "normal": (0, 40),
            "elevated": (41, 1000)
        },
        "explanation": {
            "normal": "Your liver enzyme level is normal.",
            "elevated": "Your liver enzymes are elevated. May indicate liver inflammation or damage."
        },
        "what_is_it": "Enzyme that increases when liver is damaged or inflamed"
    },
    
    # Add more common tests: TSH, Hemoglobin, WBC, etc.
}