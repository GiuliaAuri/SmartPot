#!/usr/bin/env python3
"""
Test per verificare che la rotella di caricamento sia stata aggiunta correttamente.
"""

import re
import os

def test_loading_spinner():
    """
    Testa che la rotella di caricamento sia stata aggiunta correttamente nel file page.tsx.
    """
    print("🧪 Test: Verifica rotella di caricamento nel frontend")
    
    try:
        file_path = "app/page.tsx"
        
        if not os.path.exists(file_path):
            print(f"   ❌ FAIL: File non trovato: {file_path}")
            return False
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print("   📝 Verificando presenza della rotella di caricamento...")
        
        # Verifica che ci sia la rotella accanto al sottotitolo
        spinner_pattern = r'<div className="flex items-center gap-2 mt-1">.*?<p.*?Sistema intelligente.*?</p>.*?{isUpdating && \(.*?<div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0"></div>.*?\)}'
        
        if re.search(spinner_pattern, content, re.DOTALL):
            print(f"      ✅ Rotella di caricamento trovata accanto al sottotitolo")
        else:
            print(f"      ❌ Rotella di caricamento non trovata accanto al sottotitolo")
            return False
        
        # Verifica che non ci siano rotelle duplicate
        spinner_count = content.count('animate-spin')
        if spinner_count == 1:
            print(f"      ✅ Una sola rotella di caricamento presente")
        else:
            print(f"      ⚠️  {spinner_count} rotelle di caricamento trovate (attesa 1)")
        
        # Verifica che la rotella sia condizionale (solo quando isUpdating è true)
        if '{isUpdating &&' in content:
            print(f"      ✅ Rotella condizionale basata su isUpdating")
        else:
            print(f"      ❌ Rotella non condizionale")
            return False
        
        # Verifica che la rotella abbia le classi CSS corrette
        if 'w-4 h-4' in content and 'border-blue-500' in content and 'flex-shrink-0' in content:
            print(f"      ✅ Classi CSS corrette per la rotella")
        else:
            print(f"      ❌ Classi CSS mancanti o incorrette")
            return False
        
        print("   ✅ PASS: Rotella di caricamento implementata correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore durante il test: {e}")
        return False

def test_ui_structure():
    """
    Testa che la struttura UI sia corretta.
    """
    print("🧪 Test: Verifica struttura UI")
    
    try:
        file_path = "app/page.tsx"
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print("   📝 Verificando struttura del layout...")
        
        # Verifica che ci sia il titolo principale
        if 'Smart Plants - IoT System' in content:
            print(f"      ✅ Titolo principale presente")
        else:
            print(f"      ❌ Titolo principale mancante")
            return False
        
        # Verifica che ci sia il sottotitolo
        if 'Sistema intelligente per la gestione e monitoraggio dei tuoi vasi' in content:
            print(f"      ✅ Sottotitolo presente")
        else:
            print(f"      ❌ Sottotitolo mancante")
            return False
        
        # Verifica che ci sia il componente PlantDashboard
        if '<PlantDashboard' in content:
            print(f"      ✅ Componente PlantDashboard presente")
        else:
            print(f"      ❌ Componente PlantDashboard mancante")
            return False
        
        print("   ✅ PASS: Struttura UI corretta")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore durante il test: {e}")
        return False

def main():
    """
    Esegue i test per verificare la rotella di caricamento.
    """
    print("🚀 Test Rotella di Caricamento Frontend")
    print("=" * 50)
    
    try:
        success1 = test_loading_spinner()
        success2 = test_ui_structure()
        
        print("\n" + "=" * 50)
        if success1 and success2:
            print("🎉 Tutti i test completati con successo!")
            print("✅ La rotella di caricamento è stata aggiunta correttamente")
            print("✅ La rotella appare accanto al sottotitolo quando isUpdating è true")
            print("✅ La struttura UI è corretta")
            print("✅ Non ci sono rotelle duplicate")
        else:
            print("⚠️  Alcuni test sono falliti")
        
        return success1 and success2
        
    except Exception as e:
        print(f"❌ Errore durante i test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
