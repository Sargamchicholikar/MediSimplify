import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Check if key is loaded
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    print(f"✅ API Key loaded: {api_key[:20]}...")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ API Key NOT found!")
    print("   Make sure .env file is in backend/ folder")

# Test Groq connection
import requests

try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "user", "content": "Say 'Hello!' in 3 words"}
            ],
            "max_tokens": 50
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        reply = data['choices'][0]['message']['content']
        print(f"\n✅ Groq API works! Response: {reply}")
    else:
        print(f"\n❌ Groq API error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Connection error: {e}")