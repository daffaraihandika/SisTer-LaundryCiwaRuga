# subClient.py

import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print(f"Message received: {str(message.payload.decode('utf-8'))}")

broker_address = "localhost"
print("creating new instance")

client = mqtt.Client(client_id="Client 1", protocol=mqtt.MQTTv311)
client.on_message = on_message

client.connect(broker_address, port=1883)

client.loop_start()

# Subscribe to the topics
client.subscribe("laundry")

print("Subscribed to topic 'laundry'")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()
