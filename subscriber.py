<<<<<<< ours
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to broker")
    client.subscribe("test/topic")

def on_message(client, userdata, msg):
    print(f"Received: {msg.payload.decode()}")

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()


||||||| base
=======
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to broker")
    client.subscribe("test/topic")

def on_message(client, userdata, msg):
    print(f"Received: {msg.payload.decode()}")

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
>>>>>>> theirs
