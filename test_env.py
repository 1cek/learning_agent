import os
from dotenv import load_dotenv

load_dotenv()  # Load the .env file

# Try to fetch your SerpAPI key
api_key = os.getenv("SERPAPI_KEY")

if api_key:
    print("✅ SERPAPI_KEY loaded successfully:", api_key[:5] + "..." + api_key[-5:])
else:
    print("❌ SERPAPI_KEY not found. Check your .env file or environment setup.")