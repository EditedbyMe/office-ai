import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-flash-latest"
]

def test_model(model_name, use_grounding=False):
    print(f"\nTesting {model_name} (Grounding: {use_grounding})...")
    try:
        if use_grounding:
            tools = [{'google_search_retrieval': {}}]
            model = genai.GenerativeModel(model_name=model_name, tools=tools)
        else:
            model = genai.GenerativeModel(model_name=model_name)
        
        response = model.generate_content("Hello, who are you?")
        print(f"Success! Response: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

for m in models_to_test:
    if test_model(m, use_grounding=False):
        test_model(m, use_grounding=True)
