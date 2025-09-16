#!/usr/bin/env python3
"""
Simulatore Arduino per testare il bridge senza hardware fisico.
Simula l'invio di dati sensori via seriale.
"""

import serial
import time
import random

def simulate_arduino_data(port="COM5", baudrate=9600):
    """Simula i dati che Arduino invierebbe via seriale."""
    
    print(f"🤖 Simulatore Arduino - Porta: {port}")
    print("=" * 50)
    
    try:
        # Prova a connettersi alla porta seriale
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ Connesso alla porta {port}")
        
        # Simula dati sensori
        sensor_types = ['H', 'T', 'L', 'B']  # Humidity, Temperature, Lightness, Battery
        sensor_names = ['humidity', 'temperature', 'lightness', 'battery_level']
        
        while True:
            # Genera dati casuali per i sensori
            num_sensors = random.randint(1, 3)  # 1-3 sensori per pacchetto
            
            # Inizia pacchetto
            packet = bytearray([0xFF])  # Header
            packet.append(num_sensors)  # Numero sensori
            
            print(f"📦 Invio pacchetto con {num_sensors} sensori:")
            
            for i in range(num_sensors):
                sensor_type = random.choice(sensor_types)
                sensor_value = random.randint(20, 80)  # Valore casuale
                
                packet.append(ord(sensor_type))  # Tipo sensore
                packet.append(sensor_value)      # Valore sensore
                
                sensor_name = sensor_names[sensor_types.index(sensor_type)]
                print(f"   {sensor_name} ({sensor_type}): {sensor_value}")
            
            packet.append(0xFE)  # Footer
            
            # Invia il pacchetto
            ser.write(packet)
            print(f"📤 Pacchetto inviato: {packet.hex()}")
            
            # Aspetta prima del prossimo pacchetto
            time.sleep(5)
            
    except serial.SerialException as e:
        print(f"❌ Errore porta seriale: {e}")
        print("💡 Suggerimenti:")
        print("   - Verifica che la porta sia corretta")
        print("   - Assicurati che nessun altro programma usi la porta")
        print("   - Prova a cambiare porta nel config.ini")
        
    except KeyboardInterrupt:
        print("\n🛑 Simulatore interrotto")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    # Porta di default, può essere cambiata
    PORT = "COM5"
    
    print("🤖 Simulatore Arduino")
    print("Questo programma simula i dati che Arduino invierebbe via seriale")
    print("per testare il bridge senza hardware fisico.")
    print()
    
    simulate_arduino_data(PORT)
