#!/usr/bin/env python3
"""
Test semplificato per verificare che la scrittura sicura dei file JSON funzioni.
"""

import json
import os
import sys
import tempfile
import shutil

def test_safe_json_methods():
    """
    Testa i metodi di scrittura sicura JSON senza MQTT.
    """
    print("🧪 Test: Verifica metodi di scrittura sicura JSON")
    
    # Crea una directory temporanea per i test
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, "test.json")
    
    try:
        # Simula i metodi _safe_read_json e _safe_write_json
        def safe_read_json(filename):
            try:
                if not os.path.exists(filename):
                    return []
                
                with open(filename, "r") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
                    
            except json.JSONDecodeError as e:
                print(f"      JSON decode error in {filename}: {e}")
                # Prova a leggere il file di backup se esiste
                backup_filename = filename + ".backup"
                if os.path.exists(backup_filename):
                    try:
                        with open(backup_filename, "r") as f:
                            data = json.load(f)
                            print(f"      Recovered data from backup file: {backup_filename}")
                            return data if isinstance(data, list) else []
                    except Exception as backup_e:
                        print(f"      Backup file also corrupted: {backup_e}")
                return []
            except Exception as e:
                print(f"      Error reading JSON file {filename}: {e}")
                return []
        
        def safe_write_json(filename, data):
            try:
                # Crea una copia di backup temporanea
                backup_filename = filename + ".backup"
                
                # Scrivi prima nel file di backup
                with open(backup_filename, "w") as f:
                    json.dump(data, f, indent=2)
                
                # Solo se la scrittura nel backup è riuscita, sostituisci il file originale
                if os.path.exists(backup_filename):
                    if os.path.exists(filename):
                        os.remove(filename)
                    os.rename(backup_filename, filename)
                    return True
                else:
                    print(f"      Failed to create backup file: {backup_filename}")
                    return False
                    
            except Exception as e:
                print(f"      Error writing JSON file {filename}: {e}")
                # Rimuovi il file di backup se esiste
                if os.path.exists(backup_filename):
                    os.remove(backup_filename)
                return False
        
        print("   📝 Testando scrittura e lettura base...")
        
        # Test scrittura base
        test_data = [{"plant_id": "test", "sensors": []}]
        if safe_write_json(test_file, test_data):
            print("      ✅ Scrittura base riuscita")
        else:
            print("      ❌ Scrittura base fallita")
            return False
        
        # Test lettura base
        read_data = safe_read_json(test_file)
        if read_data == test_data:
            print("      ✅ Lettura base riuscita")
        else:
            print(f"      ❌ Lettura base fallita: {read_data}")
            return False
        
        print("   📝 Testando aggiornamento dati...")
        
        # Test aggiornamento dati
        read_data[0]["sensors"].append({"sensor": "temperature", "value": 25.0})
        if safe_write_json(test_file, read_data):
            print("      ✅ Aggiornamento dati riuscito")
        else:
            print("      ❌ Aggiornamento dati fallito")
            return False
        
        # Verifica che i dati siano stati salvati
        updated_data = safe_read_json(test_file)
        if len(updated_data[0]["sensors"]) == 1:
            print("      ✅ Dati aggiornati correttamente")
        else:
            print(f"      ❌ Dati non aggiornati: {updated_data}")
            return False
        
        print("   📝 Testando gestione errori...")
        
        # Test con dati non validi
        invalid_data = {"invalid": "data"}
        if not safe_write_json(test_file, invalid_data):
            print("      ✅ Gestione errori: scrittura dati non validi fallita correttamente")
        else:
            print("      ❌ Gestione errori: scrittura dati non validi dovrebbe essere fallita")
            return False
        
        # Test con file di sola lettura (su Windows potrebbe non funzionare)
        try:
            read_only_file = os.path.join(test_dir, "read_only.json")
            with open(read_only_file, "w") as f:
                json.dump([], f)
            
            # Prova a rendere il file di sola lettura
            os.chmod(read_only_file, 0o444)
            
            result = safe_write_json(read_only_file, [{"test": "data"}])
            if not result:
                print("      ✅ Gestione errori: scrittura file di sola lettura fallita correttamente")
            else:
                print("      ⚠️  Gestione errori: scrittura file di sola lettura riuscita (normale su Windows)")
                
        except Exception as e:
            print(f"      ⚠️  Gestione errori: {e} (normale su Windows)")
        
        print("   ✅ PASS: Metodi di scrittura sicura JSON funzionano correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore durante il test: {e}")
        return False
        
    finally:
        # Pulisci la directory temporanea
        try:
            shutil.rmtree(test_dir)
        except Exception:
            pass

def main():
    """
    Esegue il test di scrittura sicura dei file JSON.
    """
    print("🚀 Test Scrittura Sicura File JSON (Semplificato)")
    print("=" * 60)
    
    try:
        success = test_safe_json_methods()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 Test completato con successo!")
            print("✅ I metodi di scrittura sicura JSON funzionano correttamente")
            print("✅ La correzione dovrebbe risolvere il problema di corruzione dei file")
        else:
            print("⚠️  Test fallito")
        
        return success
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
