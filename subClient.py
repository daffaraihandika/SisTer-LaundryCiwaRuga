import paho.mqtt.client as mqtt
import time
import mysql.connector
from datetime import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="laundry_db"
    )

def on_message(client, userdata, message):
    payload = str(message.payload.decode('utf-8'))
    print(f"Message received: {payload}")
    
    if message.topic == "order_updates":
        data = payload.split(',')
        order_id, username, berat, jenis, harga, estimasi, timestamp, laundry, status = data
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO orders (id, username, berat, jenis, harga, estimasi, timestamp, laundry, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE username=%s, berat=%s, jenis=%s, harga=%s, estimasi=%s, timestamp=%s, laundry=%s, status=%s', 
                       (order_id, username, berat, jenis, harga, estimasi, timestamp, laundry, status, username, berat, jenis, harga, estimasi, timestamp, laundry, status))
        conn.commit()
        conn.close()

def registrasi():
    conn = connect_db()
    cursor = conn.cursor()
    
    print("===Registrasi===")
    username = input("Masukkan username baru: ")
    cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
    if cursor.fetchone():
        print("Username sudah ada.")
        conn.close()
        return None

    password = input("Masukkan password baru: ")
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
    conn.commit()
    conn.close()
    print("Registrasi berhasil.")

    # Publish user registration to synchronize with server
    client.publish("user_updates", f"{username},{password},new")

    return username

def autentikasi():
    conn = connect_db()
    cursor = conn.cursor()
    
    print("===Login===")
    username = input("Masukkan username: ")
    password = input("Masukkan password: ")
    cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
    if cursor.fetchone():
        print("Autentikasi berhasil.")
        conn.close()
        return username
    else:
        print("Username atau password salah.")
        conn.close()
        return None

def follow_laundry(username):
    conn = connect_db()
    cursor = conn.cursor()

    # Ambil laundry yang belum diikuti oleh pengguna
    query = """
        SELECT lo.id, lo.name 
        FROM laundry_options lo
        LEFT JOIN subscriptions s ON lo.name = s.laundry AND s.username = %s
        WHERE s.laundry IS NULL
    """
    cursor.execute(query, (username,))
    laundry_options = cursor.fetchall()
    
    if not laundry_options:
        print("Anda sudah mengikuti semua laundry.")
        conn.close()
        return
    
    print("Pilih laundry yang ingin diikuti:")
    for idx, option in enumerate(laundry_options, start=1):
        print(f"{idx}. {option[1]}")
    
    print(f"{len(laundry_options) + 1}. Tidak ingin mengikuti laundry manapun")
    
    pilihan = int(input("Masukkan pilihan (nomor): "))
    
    if 1 <= pilihan <= len(laundry_options):
        laundry = laundry_options[pilihan - 1][1]
        cursor.execute('INSERT IGNORE INTO subscriptions (username, laundry) VALUES (%s, %s)', (username, laundry))
        conn.commit()
        print(f"{username} mengikuti {laundry}")
        client.subscribe(f"{laundry}/{username}")

        # Publish subscription to synchronize with server
        client.publish("subscription_updates", f"{username},{laundry},new")
    elif pilihan == len(laundry_options) + 1:
        print("Anda memilih untuk tidak mengikuti laundry manapun.")
    else:
        print("Pilihan tidak valid.")
    
    conn.close()

def get_estimasi_waktu(username, jenis_laundry):
    conn = connect_db()
    cursor = conn.cursor()
    
    query = f"""
        SELECT DISTINCT lo.name, lo.{jenis_laundry}
        FROM laundry_options lo
        JOIN subscriptions s ON lo.name = s.laundry
        WHERE s.username = %s
    """
    cursor.execute(query, (username,))
    laundry_options = cursor.fetchall()
    
    conn.close()
    
    return laundry_options

def kirim_pesanan(username):
    conn = connect_db()
    cursor = conn.cursor()
    
    berat_cucian = float(input("Masukkan berat cucian Anda (kg): "))
    
    print("Pilih jenis laundry:")
    print("1. Hemat")
    print("2. Reguler")
    print("3. Ekspres")
    jenis_pilihan = int(input("Masukkan pilihan (nomor): "))
    
    jenis_laundry = None
    if jenis_pilihan == 1:
        jenis_laundry = "hemat"
    elif jenis_pilihan == 2:
        jenis_laundry = "reguler"
    elif jenis_pilihan == 3:
        jenis_laundry = "ekspres"
    else:
        print("Pilihan tidak valid.")
        conn.close()
        return
    
    estimasi_waktu_list = get_estimasi_waktu(username, jenis_laundry)
    
    if not estimasi_waktu_list:
        print("Anda belum mengikuti laundry manapun.")
        conn.close()
        return
    
    print("Estimasi waktu selesai untuk laundry yang Anda ikuti:")
    for idx, laundry in enumerate(estimasi_waktu_list, start=1):
        print(f"{idx}. {laundry[0].capitalize()}: {laundry[1]} hari")
    
    pilihan = int(input("Masukkan pilihan laundry (nomor): "))
    
    if 1 <= pilihan <= len(estimasi_waktu_list):
        pilihan_laundry = estimasi_waktu_list[pilihan - 1][0].lower()
        estimasi = estimasi_waktu_list[pilihan - 1][1]
    else:
        print("Pilihan tidak valid.")
        conn.close()
        return
    
    harga = hitung_harga(berat_cucian, jenis_laundry)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('INSERT INTO orders (username, berat, jenis, harga, estimasi, timestamp, laundry, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
              (username, berat_cucian, jenis_laundry, harga, estimasi, timestamp, pilihan_laundry, 'new'))
    conn.commit()
    conn.close()
    print(f"Pesanan ke {pilihan_laundry.capitalize()} telah dikirim. Estimasi waktu selesai: {estimasi} hari. Harga: {harga} IDR.")
    client.publish(f"{pilihan_laundry}/{username}", f"Pesanan Anda ke {pilihan_laundry.capitalize()} telah diterima. Estimasi waktu selesai: {estimasi} hari. Harga: {harga} IDR.")

    # Publish order to synchronize with server
    client.publish("order_updates", f"{username},{berat_cucian},{jenis_laundry},{harga},{estimasi},{timestamp},{pilihan_laundry},new")

def hitung_harga(berat, jenis_laundry):
    if jenis_laundry == "hemat":
        return berat * 5000  # harga per kg untuk Hemat
    elif jenis_laundry == "reguler":
        return berat * 7000  # harga per kg untuk Reguler
    elif jenis_laundry == "ekspres":
        return berat * 10000  # harga per kg untuk Ekspres
    else:
        print("Jenis laundry tidak dikenal.")
        return None

def main():
    broker_address = "192.168.1.26"  # address of the broker
    # broker_address = "localhost"  # address of the broker
    print("creating new instance")
    global client
    client = mqtt.Client(client_id="Client 1", protocol=mqtt.MQTTv311)
    client.on_message = on_message

    client.connect(broker_address, port=1883)

    client.loop_start()

    username = None
    while not username:
        punya_akun = input("Apakah Anda sudah memiliki akun? (Y/n): ").strip().lower()
        if punya_akun == 'y':
            username = autentikasi()
        else:
            registrasi()
            username = autentikasi()

    follow_laundry(username)
    kirim_pesanan(username)

    client.subscribe("order_updates")
    client.subscribe("user_updates")
    client.subscribe("subscription_updates")

    print("Subscribed to laundry notifications and order updates")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
