# 🏥 MediSimplify

**AI-Powered Multi-Modal Medical Report Analyzer**

Making complex medical reports understandable for everyone - in 10 Indian languages with voice support.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

**Author:** [Sargam Chicholikar](https://linkedin.com/in/sargam-chicholikar)  
**Contact:** work.sargam@gmail.com  
**Created:** February 2026

---

## 🎯 The Problem

In India:
- **60%** of the population doesn't read English fluently
- **90%** of medical reports use complex English medical jargon  
- Patients receive prescriptions, lab reports, and X-rays they **can't understand**
- Elderly and rural populations have **no accessible way** to comprehend their medical information

**Result:** Patients take medicines without knowing their purpose, side effects, or proper usage.

---

## 💡 The Solution

**MediSimplify** is an AI-powered platform that analyzes three types of medical reports and explains them in simple, patient-friendly language:

### 📋 Prescription Analysis
- **Upload** printed prescription images (OCR extraction)
- **Type** drug names manually for handwritten prescriptions
- **Get** comprehensive drug information from FDA database
- **Understand** what each medicine treats, dosage, warnings

### 🩸 Lab Report Analysis  
- **Upload** PDF or image of lab report
- **AI extracts** all test values automatically (CBC, LFT, KFT, etc.)
- **Explains** each test in simple language with analogies
- **Color-coded** results (🟢 Normal, 🟠 Warning, 🔴 Attention)
- **Works with ANY test** - not limited to predefined database!

### 🔬 X-Ray Analysis
- **Upload** X-ray image
- **AI detects** fractures and identifies bones
- **Classifies** fracture type (hairline, displaced, comminuted, etc.)
- **Predicts** likely injury cause (fall, twist, sports, etc.)
- **Estimates** recovery time (4-6 weeks, 8-12 weeks, etc.)
- **Provides** clear action items

---

## ✨ Key Features

🌍 **10 Indian Languages**
- Hindi (हिन्दी), Gujarati (ગુજરાતી), Marathi (मराठी), Tamil (தமிழ்), Telugu (తెలుగు)
- Punjabi (ਪੰਜਾਬੀ), Malayalam (മലയാളം), Bengali (বাংলা), Assamese (অসমীয়া), English

🔊 **Voice Support**
- Text-to-speech in all supported languages
- Audio controls: Play, Pause, Resume, Replay, Stop
- Progress bar and time tracking
- Accessibility for elderly and visually impaired

⚡ **Lightning Fast**
- Intelligent 3-tier caching (1000x speedup on repeats)
- Parallel processing (4x faster multi-drug validation)
- 5-10s first query, <2s cached responses

🎯 **Smart Features**
- Fuzzy string matching corrects typos/OCR errors
- Detects health conditions from drug combinations
- Zero-maintenance architecture (always up-to-date)
- Comprehensive medical disclaimers

---

## 🛠️ Technology Stack

**Frontend**
- HTML5, CSS3 (Modern Glassmorphism UI)
- Vanilla JavaScript
- Responsive design

**Backend**
- Python 3.8+
- FastAPI (REST API framework)
- Uvicorn (ASGI server)
- Parallel processing (ThreadPoolExecutor)

**AI/ML Models**
- **Google Gemini 2.5 Flash** - X-ray vision analysis
- **Groq Llama 3.3 70B** - Medical text simplification
- **EasyOCR with CRAFT** - Text extraction from images

**NLP Techniques**
- Named Entity Recognition (drug name extraction)
- Fuzzy String Matching (Levenshtein distance for error correction)
- Medical text simplification
- Cross-lingual explanation generation

**External APIs**
- FDA OpenAPI (100,000+ drug database)
- Google Generative AI (Gemini)
- Groq API (LLM inference)
- gTTS (Text-to-Speech)

**Computer Vision**
- OpenCV (image preprocessing)
- PIL/Pillow (image manipulation)
- PyPDF2 (PDF text extraction)

---

## 📊 Performance Metrics

| Metric | Performance |
|--------|------------|
| **OCR Accuracy** | 85-90% (printed prescriptions) |
| **Drug Coverage** | 100,000+ medications (FDA) |
| **Lab Test Coverage** | Unlimited (AI-powered) |
| **Processing Time** | 5-10s first query, 1-2s cached |
| **Languages** | 10 Indian languages |
| **Cost to Users** | 100% FREE |
| **X-Ray Analysis** | Fracture detection + recovery prediction |

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8 or higher
pip (Python package manager)
```

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/Sargamchicholikar/MediSimplify.git
cd MediSimplify
```

**2. Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**3. Set up API keys** (Free - get from links below)
```bash
# Create .env file in backend folder
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

**Get free API keys:**
- Groq: https://console.groq.com/keys (14,400 requests/day free)
- Gemini: https://aistudio.google.com/apikey (1,500 requests/day free)

**4. Run the application**
```bash
# Start backend server
python app.py

# Backend runs on: http://127.0.0.1:8000
# Open in browser: http://127.0.0.1:8000/
```

---

## 📱 Usage

### Analyze a Prescription
1. Upload printed prescription image **OR** type drug names manually
2. Select your preferred language
3. Click "Decode My Reports"
4. Get detailed drug information in your language
5. Click 🔊 to listen via voice

### Analyze Lab Report
1. Upload lab report (PDF or image)
2. AI extracts all test values
3. Each test explained in simple terms
4. Color-coded for quick understanding

### Analyze X-Ray
1. Upload X-ray image
2. AI detects fractures, identifies bones
3. Get fracture type, recovery time, injury cause
4. Clear action items provided


## 🔬 Technical Highlights

### Zero-Maintenance Architecture
```python
# No manual database updates needed!
Drug Info: FDA API (always current)
Lab Tests: AI-powered (handles any test)
X-Rays: Vision AI (any bone/fracture)
```

### Intelligent Fuzzy Matching
```python
# Corrects OCR errors and typos
similarity = fuzz.ratio("amlodipin", "amlodipine")  # 95%
if similarity >= 75%:
    return corrected_drug_name
```

### Parallel Processing
```python
# 4x faster drug validation
with ThreadPoolExecutor(max_workers=5) as executor:
    # All drugs validated simultaneously
    futures = {executor.submit(validate, drug): drug for drug in drugs}
```

### Three-Tier Caching
```python
# 1000x speedup on repeat queries
Session Cache (0.001s) → File Cache (0.01s) → API Call (3-5s)
```

---

## 📚 Project Structure
```
MediSimplify/
├── backend/
│   ├── app.py                      # FastAPI main application
│   ├── drug_service.py             # Drug validation & FDA API
│   ├── ai_lab_analyzer.py          # Lab report AI analysis
│   ├── advanced_xray_vision.py     # X-ray vision AI
│   ├── voice_generator.py          # Text-to-speech
│   ├── drug_translator.py          # Multi-language translation
│   ├── ocr_module.py               # OCR & text extraction
│   ├── drug_database.py            # Disease detection logic
│   ├── lab_database.py             # Lab test reference (minimal)
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── index.html                  # Main application UI
│   └── about.html                  # About page
├── data/
│   ├── drug_cache.json             # Cached drug info
│   └── audio/                      # Generated audio files
├── LICENSE                         # MIT License
├── README.md                       # This file
```

---

## 🎓 Use Cases

### For Patients
- Understand prescriptions in native language
- Learn what lab test results mean
- Get X-ray fracture analysis with recovery timeline
- Listen to explanations via voice

### For Families
- Help elderly parents understand medical reports
- Translate doctor's instructions to regional languages
- Educational tool for health awareness

### For Healthcare Workers
- Explain reports to patients in rural areas
- Communication aid in multilingual settings
- Patient education tool

---

## 🔮 Future Enhancements

- [ ] 📱 Mobile application (React Native)
- [ ] 🤖 Custom ML models trained on Indian medical data
- [ ] 🎨 Animated visual explanations (healing timelines, annotated X-rays)
- [ ] 💬 Conversational AI chatbot for Q&A
- [ ] 🩺 Sonography/ultrasound analysis
- [ ] ✍️ Handwriting recognition with confirmation
- [ ] 📊 Patient health tracking dashboard
- [ ] 🌐 Offline mode for low-connectivity areas

---

## 🤝 Contributing

Contributions are welcome! This project aims to improve healthcare accessibility in India.

**How to contribute:**
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Areas for contribution:**
- Additional Indian languages (Kannada, Odia, etc.)
- UI/UX improvements
- OCR accuracy enhancements
- Documentation and tutorials
- Testing with real medical reports
- Mobile app development

---

## ⚠️ Important Disclaimer

**CRITICAL:** This tool is for **educational purposes only**. 

It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. 

- ❌ Do not use for medical decision-making
- ❌ Do not stop/change medications based on this tool
- ✅ Always consult qualified healthcare professionals
- ✅ Use as educational supplement only

The AI analysis is based on general medical knowledge and may not account for:
- Individual patient circumstances
- Drug interactions specific to your health
- Contraindications or allergies
- Latest medical guidelines

**Always verify information with licensed medical professionals.**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2026 Sargam Chicholikar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software... [see LICENSE file for full text]
```

**Attribution Required:** If you use this work, please provide clear attribution.

---

## 👩‍💻 About the Developer

**Sargam Chicholikar**

- 🎓 B.Tech Computer Engineering, Bharati Vidyapeeth University (CGPA: 8.93/10)
- 💼 Former Software Developer Intern at U.R.S.C (ISRO), Bengaluru
- 📝 Research: Sentiment Analysis for Stock Market Prediction using FinBERT (IEEE, under review)
- 🌟 Volunteer: Medical camps, Blood donation drives, NSS, GDSC

**Motivation:** This project was inspired by volunteering at Ayush Social Welfare Trust Medical Camp 
in Valia, Gujarat, where I witnessed firsthand how language barriers and medical jargon prevent 
patients from understanding their own health information.

**Contact:**
- 📧 Email: work.sargam@gmail.com
- 💼 LinkedIn: [sargam-chicholikar](https://linkedin.com/in/sargam-chicholikar)
- 🐙 GitHub: [Sargamchicholikar](https://github.com/Sargamchicholikar)

---

## 🙏 Acknowledgments

- Medical camp volunteers who inspired this project
- Patients who shared their struggles with medical reports
- Open-source community for incredible tools (FastAPI, EasyOCR, etc.)
- Bharati Vidyapeeth University for academic support
- ISRO for internship experience that shaped my technical approach

---

## 📊 Project Stats

- **Lines of Code:** ~3,500+
- **Files:** 15+ Python/HTML files
- **AI Models Integrated:** 3 (EasyOCR, Groq, Gemini)
- **Languages Supported:** 10
- **Development Time:** 2 weeks (Feb 2026)
- **Testing:** 50+ real medical reports

---

## 🌟 Why This Project Matters

Healthcare information should be a **right**, not a **privilege** that requires English literacy and medical knowledge.

By combining Computer Vision, NLP, and LLMs with a focus on accessibility, MediSimplify demonstrates how AI can democratize healthcare information access across linguistic and literacy barriers.

**Impact Potential:**
- Improve medication adherence
- Reduce medical errors from miscommunication
- Empower informed health decisions
- Bridge urban-rural healthcare gap
- Support elderly and low-literacy populations

---

## 🏆 Recognition & Usage

**Academic:** Independent research project for AI/ML portfolio  
**Purpose:** Demonstrates practical application of multi-modal AI in healthcare  
**Audience:** Patients, families, community health workers in India  

**If this project helps you or inspires your work, please:**
- ⭐ Star this repository
- 🔄 Share with others who might benefit
- 📝 Cite this work in academic contexts
- 💬 Provide feedback for improvements

---

## 📞 Support & Feedback

Found a bug? Have a suggestion? Want to collaborate?

- 🐛 [Report Issues](https://github.com/Sargamchicholikar/MediSimplify/issues)
- 💡 [Feature Requests](https://github.com/Sargamchicholikar/MediSimplify/issues)
- 📧 Email: work.sargam@gmail.com

---

## 📖 Documentation

- [Development Log](DEVELOPMENT_LOG.md) - Complete development timeline
- [About Page](https://medisimplify.com/about) - Story & inspiration
- [API Documentation](http://127.0.0.1:8000/docs) - FastAPI auto-generated docs

---

## 🎓 Academic Context

This project is part of my portfolio demonstrating:
- Multi-modal AI system design
- Production-level API integration
- Healthcare domain application
- Cross-lingual NLP
- Computer Vision applications

**Intended for:** MS applications, job interviews, research collaboration

---

## 📜 Copyright & Attribution

**© 2026 Sargam Chicholikar. All rights reserved.**

Original work created January 2026. While open-sourced under MIT License, 
this represents original research and development by Sargam Chicholikar.

**Unique Contributions:**
- Multi-modal medical AI architecture
- Zero-maintenance healthcare database approach
- Patient-centric X-ray analysis with recovery prediction
- Cross-lingual medical simplification system

**For commercial use or derivative works, proper attribution is required as per MIT License.**

---

**Built with ❤️ for better healthcare accessibility in India**

*Dedicated to every patient who struggled to understand their medical reports,  
and to the medical camp volunteers who showed me this problem needed solving.*

---

## ⭐ If you found this helpful, please star the repo!

Every star helps increase visibility and validates the work put into making 
healthcare information accessible for everyone.

**[Star this repo](https://github.com/Sargamchicholikar/MediSimplify)** ⭐
```

---

## Now Create `requirements.txt`

**Create:** `backend/requirements.txt`
```
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.9
pydantic==2.5.3
requests==2.31.0
python-dotenv==1.0.0
easyocr==1.7.0
opencv-python==4.9.0.80
pillow==10.2.0
pypdf2==3.0.1
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0
gtts==2.5.0
google-generativeai==0.3.2
