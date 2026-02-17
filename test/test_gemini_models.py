import google.generativeai as genai

api_key = "AIzaSyA84_aMK-3gY1MKKtp1QKaNqKYuNaFjIVQ"
genai.configure(api_key=api_key)

print("Available Gemini models:")
print("="*60)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✅ {m.name}")
        print(f"   Supports: {m.supported_generation_methods}")
        print()

print("="*60)