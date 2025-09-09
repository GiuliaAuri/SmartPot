#!/usr/bin/env python3
"""
Test script per l'endpoint GET /api/status
"""

import requests
import json
from datetime import datetime

def test_api_status():
    """Testa l'endpoint /api/status"""
    
    url = "http://127.0.0.1:5000/api/status"
    
    try:
        print(f"Testing {url}...")
        response = requests.get(url, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Errore: Impossibile connettersi al server")
        print("Assicurati che il backend sia attivo (python app.py)")
    except requests.exceptions.Timeout:
        print("❌ Errore: Timeout della richiesta")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_api_status()
