FROM python:3.10-slim

# Install system dependencies for OCR and Graphics
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies (This handles the 5GB of ML libraries)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Hugging Face runs on port 7860
CMD ["uvicorn", "backend.index:app", "--host", "0.0.0.0", "--port", "7860"]
