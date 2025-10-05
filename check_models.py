import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the API key from your .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Checking for available models that support 'generateContent' ---")

# List all available models and check their supported methods
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Model found: {m.name}")

print("--- Check complete ---")