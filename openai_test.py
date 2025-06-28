#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv('/app/backend/.env')

# Get OpenAI API key
api_key = os.environ.get('OPENAI_API_KEY')
print(f"OpenAI API Key: {api_key[:4]}...{api_key[-4:]}")

# Print OpenAI version
print(f"OpenAI package version: {openai.__version__}")

# Try to initialize the client
try:
    client = openai.OpenAI(api_key=api_key)
    print("✅ Successfully initialized OpenAI client")
except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {e}")

# Try to initialize the client with proxies parameter
try:
    client = openai.OpenAI(api_key=api_key, proxies=None)
    print("✅ Successfully initialized OpenAI client with proxies=None")
except Exception as e:
    print(f"❌ Failed to initialize OpenAI client with proxies=None: {e}")