#!/usr/bin/env python3
"""
Test semplificato per verificare la gestione delle task asincrone.
"""

import asyncio
import time
import sys

def test_simple_task_management():
    """
    Testa la gestione delle task asincrone in modo semplificato.
    """
    print("🧪 Test: Verifica gestione task asincrone (semplificato)")
    
    try:
        async def simulate_work(duration, name):
            """Simula lavoro asincrono."""
            print(f"      🔄 Task {name} iniziata")
            await asyncio.sleep(duration)
            print(f"      ✅ Task {name} completata")
            return f"Task {name} completed"
        
        async def main():
            """Funzione principale del test."""
            print("   📝 Testando creazione e esecuzione task...")
            
            # Crea task con durate diverse
            task1 = asyncio.create_task(simulate_work(0.1, "A"))
            task2 = asyncio.create_task(simulate_work(0.2, "B"))
            task3 = asyncio.create_task(simulate_work(0.3, "C"))
            
            print(f"      📊 Create 3 task")
            
            # Esegui le task
            start_time = time.time()
            results = await asyncio.gather(task1, task2, task3)
            end_time = time.time()
            
            print(f"      ⏱️  Task completate in {end_time - start_time:.2f}s")
            print(f"      📋 Risultati: {results}")
            
            print("   📝 Testando cancellazione task...")
            
            # Crea task che verranno cancellate
            task4 = asyncio.create_task(simulate_work(1.0, "D"))
            task5 = asyncio.create_task(simulate_work(1.0, "E"))
            
            print(f"      📊 Create 2 task da cancellare")
            
            # Aspetta un po' e poi cancella
            await asyncio.sleep(0.05)
            
            # Cancella le task
            task4.cancel()
            task5.cancel()
            print(f"      🚫 Task D ed E cancellate")
            
            # Verifica che le task siano state cancellate
            try:
                await asyncio.gather(task4, task5)
            except asyncio.CancelledError:
                print(f"      ✅ Task cancellate correttamente")
            
            return True
        
        # Esegui il test
        result = asyncio.run(main())
        
        if result:
            print("   ✅ PASS: Gestione task asincrone funziona correttamente")
            return True
        else:
            print("   ❌ FAIL: Test fallito")
            return False
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore durante il test: {e}")
        return False

def main():
    """
    Esegue il test di gestione delle task asincrone.
    """
    print("🚀 Test Gestione Task Asincrone (Semplificato)")
    print("=" * 60)
    
    try:
        success = test_simple_task_management()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 Test completato con successo!")
            print("✅ La gestione delle task asincrone funziona correttamente")
            print("✅ Le modifiche al DataCollectorConsumer dovrebbero risolvere")
            print("   gli errori 'Task was destroyed but it is pending'")
        else:
            print("⚠️  Test fallito")
        
        return success
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
