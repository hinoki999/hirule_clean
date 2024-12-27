import paho.mqtt.client as mqtt
from time import sleep

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.connect("localhost", 1883, 60)

while True:
    client.publish("test/topic", "Hello MQTT")
    sleep(2)