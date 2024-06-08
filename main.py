import logging
import mysql.connector
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="laundry_db"
    )

def on_message(client, userdata, message):
    payload = str(message.payload.decode('utf-8'))
    # print(f"Message received: {payload}")

    conn = connect_db()
    cursor = conn.cursor()

    data = payload.split(',')
    # logging.debug(f"Data split: {data}")

    # Memastikan jumlah elemen sesuai untuk berbagai jenis pesan
    if message.topic == "user_updates":
        if len(data) == 3:
            username, password, status = data
            if status == 'new':
                cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
                conn.commit()
        else:
            logging.error(f"Data length mismatch for user_updates. Expected 3, got {len(data)}")

    elif message.topic == "subscription_updates":
        if len(data) == 3:
            username, laundry, status = data
            if status == 'new':
                cursor.execute('INSERT INTO subscriptions (username, laundry) VALUES (%s, %s)', (username, laundry))
                conn.commit()
        else:
            logging.error(f"Data length mismatch for subscription_updates. Expected 3, got {len(data)}")

    elif message.topic == "order_updates":
        if len(data) == 8:
            username, berat, jenis, harga, estimasi, timestamp, laundry, status = data
            if laundry == selected_laundry:  # Only process orders for the selected laundry
                cursor.execute('INSERT INTO orders (username, berat, jenis, harga, estimasi, timestamp, laundry, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=%s, berat=%s, jenis=%s, harga=%s, estimasi=%s, timestamp=%s, laundry=%s, status=%s', 
                               (username, berat, jenis, harga, estimasi, timestamp, laundry, status, username, berat, jenis, harga, estimasi, timestamp, laundry, status))
                conn.commit()
        else:
            logging.error(f"Data length mismatch for order_updates. Expected 8, got {len(data)}")

    conn.close()

def autentikasi_laundry():
    laundry_name = input("Masukkan nama laundry (Laundry Ciwa/Laundry Ruga): ").strip()
    if laundry_name in ["Laundry Ciwa", "Laundry Ruga"]:
        return laundry_name
    else:
        print("Nama laundry tidak valid.")
        return None

def kirim_info_penjemputan(laundry_name, username):
    conn = connect_db()
    cursor = conn.cursor()

    waktu_penjemputan = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pesan = f"{laundry_name.capitalize()} akan menjemput baju kotor pada {waktu_penjemputan}."
    client.publish(f"{laundry_name}/{username}", pesan)
    print(f"Pesan dikirim ke {username}: {pesan}")

    conn.close()

def kirim_info_pengantaran(laundry_name, username, estimasi):
    waktu_pengantaran = (datetime.now() + timedelta(days=estimasi)).strftime('%Y-%m-%d %H:%M:%S')
    pesan = f"{laundry_name.capitalize()} akan mengantarkan baju hasil laundry pada {waktu_pengantaran}."
    client.publish(f"{laundry_name}/{username}", pesan)
    print(f"Pesan dikirim ke {username}: {pesan}")

def process_orders(laundry_name):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE laundry=%s AND status=%s', (laundry_name, 'new'))
    orders = cursor.fetchall()
    # print(orders)

    if not orders:
        print(f"Tidak ada pesanan baru untuk {laundry_name}.")
        conn.close()
        return

    for order in orders:
        order_id = order[0]
        username = order[1]
        estimasi = order[5]
        kirim_info_penjemputan(laundry_name, username)
        kirim_info_pengantaran(laundry_name, username, estimasi)
        cursor.execute('UPDATE orders SET status=%s WHERE id=%s', ('in progress', order_id))
        conn.commit()
        
        # Publish order update to synchronize with client
        client.publish("order_updates", f"{username},{order[2]},{order[3]},{order[4]},{estimasi},{order[6]},{laundry_name},in progress")

    conn.close()

def main():
    broker_address = "192.168.1.33"  # address of the broker
    print("creating new instance")
    global client
    client = mqtt.Client(client_id="Laundry Service", protocol=mqtt.MQTTv311)
    client.on_message = on_message
    print("connecting to broker")
    client.connect(broker_address, port=1883)

    global selected_laundry
    selected_laundry = None
    while not selected_laundry:
        selected_laundry = autentikasi_laundry()

    client.subscribe("order_updates")
    client.subscribe("user_updates")
    client.subscribe("subscription_updates")
    client.subscribe(f"{selected_laundry}/#")  # Subscribe to relevant notifications

    client.loop_start()

    while True:
        action = input(f"Masukkan aksi untuk {selected_laundry.capitalize()} (proses/keluar): ").strip().lower()
        if action == "proses":
            process_orders(selected_laundry)
        elif action == "keluar":
            break
        else:
            print("Aksi tidak dikenal.")

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()