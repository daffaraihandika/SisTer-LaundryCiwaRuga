import paho.mqtt.client as mqtt
import time

broker_address = "localhost"
print("creating new instance")
client = mqtt.Client(client_id="Laundry Bojong", protocol=mqtt.MQTTv311)
print("connecting to broker")
client.connect(broker_address, port=1883)

client.loop_start()

inputs = ""

while inputs.lower() != "y":
    jemputBaju = int(input("Masukkan estimasi waktu penjemputan baju kotor (jam): "))
    sendBaju = int(input("Masukkan estimasi waktu pengiriman baju hasil laundry (jam): "))
    totalBaju = jemputBaju + sendBaju
    
    client.publish("bojong", "Selamat datang di laundry bojong")
    client.publish("bojong", f"Estimasi waktu penjemputan baju kotor selama {jemputBaju} jam")
    client.publish("bojong", f"Estimasi waktu pengiriman baju hasil laundry selama {sendBaju} jam")
    client.publish("bojong", f"Total waktu baju hasil laundry selama {totalBaju} jam")
    
    print("Apakah sudah semua? (Y/n) ", end= " ")
    inputs = input()

client.loop_stop()
