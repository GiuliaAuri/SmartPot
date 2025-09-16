import paho.mqtt.publish as publish
publish.single("RVactuator/0", "120", hostname="localhost", port=7883) # acceso
publish.single("RVactuator/0", "50", hostname="localhost", port=7883) # spegnimento
