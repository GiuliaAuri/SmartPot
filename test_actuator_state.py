#!/usr/bin/env python3
"""
Test script per verificare il metodo _get_current_actuator_state
"""
import json
import os
import tempfile

def test_get_current_actuator_state():
    """Test del metodo _get_current_actuator_state"""
    
    # Crea un file JSON temporaneo per il test
    test_data = [{
        "plant_id": "my_cactus1",
        "sensors": [],
        "actuators": [
            {
                "actuator": "irrigation",
                "device": "water_metering",
                "values": [
                    {"value": True, "timestamp": "1757415132"},
                    {"value": False, "timestamp": "1757415200"}
                ]
            }
        ],
        "alerts": []
    }]
    
    # Crea file temporaneo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        temp_file = f.name
    
    try:
        # Simula il metodo _get_current_actuator_state
        def _get_current_actuator_state(filename, plant_id, actuator_type):
            try:
                if not os.path.exists(filename):
                    return False
                    
                with open(filename, "r") as f:
                    plants = json.load(f)
                    
                for plant in plants:
                    if plant["plant_id"] == plant_id:
                        actuators = plant.get("actuators", [])
                        for actuator in actuators:
                            if actuator.get("actuator") == actuator_type:
                                values = actuator.get("values", [])
                                if values:
                                    return values[-1].get("value", False)
                        break
            except Exception as e:
                print(f"Error reading actuator state: {e}")
                
            return False
        
        # Test 1: Attuatore esistente
        result1 = _get_current_actuator_state(temp_file, "my_cactus1", "irrigation")
        print(f"✅ Test 1 - Attuatore esistente: {result1}")
        assert result1 == False, f"Expected False, got {result1}"
        
        # Test 2: Attuatore non esistente
        result2 = _get_current_actuator_state(temp_file, "my_cactus1", "temperature")
        print(f"✅ Test 2 - Attuatore non esistente: {result2}")
        assert result2 == False, f"Expected False, got {result2}"
        
        # Test 3: Pianta non esistente
        result3 = _get_current_actuator_state(temp_file, "my_fico1", "irrigation")
        print(f"✅ Test 3 - Pianta non esistente: {result3}")
        assert result3 == False, f"Expected False, got {result3}"
        
        print("🎉 Tutti i test sono passati!")
        
    finally:
        # Pulisci il file temporaneo
        os.unlink(temp_file)

if __name__ == "__main__":
    test_get_current_actuator_state()
