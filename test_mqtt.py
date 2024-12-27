import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.loop_start()