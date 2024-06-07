import mysql.connector
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="laundry_db"
    )

def autentikasi_laundry():
    laundry_name = input("Masukkan nama laundry (Laundry Ciwa/ Laundry Ruga): ").strip().lower()
    if laundry_name in ["laundry ciwa", "laundry ruga"]:
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
        client.publish("order_updates", f"{order_id},{username},{order[2]},{order[3]},{order[4]},{estimasi},{order[6]},{laundry_name},in progress")
    
    conn.close()

def main():
    broker_address = "192.168.1.26"  # address of the broker
    # broker_address = "localhost"  # address of the broker
    print("creating new instance")
    global client
    client = mqtt.Client(client_id="Laundry Service", protocol=mqtt.MQTTv311)
    print("connecting to broker")
    client.connect(broker_address, port=1883)

    client.loop_start()

    laundry_name = None
    while not laundry_name:
        laundry_name = autentikasi_laundry()

    while True:
        action = input("Masukkan aksi (proses/keluar): ").strip().lower()
        if action == "proses":
            process_orders(laundry_name)
        elif action == "keluar":
            break
        else:
            print("Aksi tidak dikenal.")

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
