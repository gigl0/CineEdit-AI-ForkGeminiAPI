import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carica la chiave dal file .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERRORE: Chiave non trovata nel file .env")
else:
    genai.configure(api_key=api_key)
    
    print("--- MODELLI DISPONIBILI PER TE ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Errore di connessione: {e}")