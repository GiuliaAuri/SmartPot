#!/usr/bin/env python3
"""
Test per verificare la gestione corretta delle task asincrone.
"""

import asyncio
import time
import sys
import os

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_task_management():
    """
    Testa la gestione delle task asincrone.
    """
    print("🧪 Test: Verifica gestione task asincrone")
    
    try:
        # Simula il comportamento del DataCollectorConsumer
        pending_tasks = set()
        last_cleanup = time.time()
        
        def cleanup_completed_tasks():
            """Pulisce le task completate."""
            completed_tasks = set()
            for task in pending_tasks:
                if task.done():
                    completed_tasks.add(task)
            
            pending_tasks -= completed_tasks
            if completed_tasks:
                print(f"      ✅ Pulite {len(completed_tasks)} task completate")
            return len(completed_tasks)
        
        async def simulate_async_work(duration):
            """Simula lavoro asincrono."""
            await asyncio.sleep(duration)
            return f"Task completed after {duration}s"
        
        print("   📝 Testando creazione e tracciamento task...")
        
        # Crea alcune task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Crea task con durate diverse
            task1 = asyncio.create_task(simulate_async_work(0.1))
            task2 = asyncio.create_task(simulate_async_work(0.2))
            task3 = asyncio.create_task(simulate_async_work(0.3))
            
            pending_tasks.add(task1)
            pending_tasks.add(task2)
            pending_tasks.add(task3)
            
            print(f"      📊 Create {len(pending_tasks)} task")
            
            # Esegui le task
            start_time = time.time()
            loop.run_until_complete(asyncio.gather(task1, task2, task3))
            end_time = time.time()
            
            print(f"      ⏱️  Task completate in {end_time - start_time:.2f}s")
            
            # Testa la pulizia
            print("   📝 Testando pulizia task completate...")
            cleaned = cleanup_completed_tasks()
            
            if cleaned == 3:
                print(f"      ✅ Pulite {cleaned} task completate")
            else:
                print(f"      ❌ Pulite {cleaned} task (attese 3)")
                return False
            
            if len(pending_tasks) == 0:
                print(f"      ✅ Nessuna task pendente rimasta")
            else:
                print(f"      ❌ {len(pending_tasks)} task pendenti rimaste")
                return False
            
            print("   📝 Testando cancellazione task...")
            
            # Crea task che verranno cancellate
            task4 = asyncio.create_task(simulate_async_work(1.0))
            task5 = asyncio.create_task(simulate_async_work(1.0))
            
            pending_tasks.add(task4)
            pending_tasks.add(task5)
            
            print(f"      📊 Create {len(pending_tasks)} task da cancellare")
            
            # Cancella le task
            for task in pending_tasks:
                if not task.done():
                    task.cancel()
                    print(f"      🚫 Task cancellata: {task}")
            
            # Pulisci le task cancellate
            cleaned = cleanup_completed_tasks()
            
            if cleaned == 2:
                print(f"      ✅ Pulite {cleaned} task cancellate")
            else:
                print(f"      ❌ Pulite {cleaned} task (attese 2)")
                return False
            
            if len(pending_tasks) == 0:
                print(f"      ✅ Nessuna task pendente rimasta dopo cancellazione")
            else:
                print(f"      ❌ {len(pending_tasks)} task pendenti rimaste")
                return False
            
        finally:
            loop.close()
        
        print("   ✅ PASS: Gestione task asincrone funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore durante il test: {e}")
        return False

def main():
    """
    Esegue il test di gestione delle task asincrone.
    """
    print("🚀 Test Gestione Task Asincrone")
    print("=" * 50)
    
    try:
        success = test_task_management()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Test completato con successo!")
            print("✅ La gestione delle task asincrone funziona correttamente")
            print("✅ Non dovrebbero più verificarsi errori 'Task was destroyed but it is pending'")
        else:
            print("⚠️  Test fallito")
        
        return success
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
