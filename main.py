# main.py

import mysql.connector
from datetime import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="laundry_db"
    )

def registrasi():
    conn = connect_db()
    cursor = conn.cursor()
    
    username = input("Masukkan username baru: ")
    cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
    if cursor.fetchone():
        print("Username sudah ada.")
        conn.close()
        return

    password = input("Masukkan password baru: ")
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
    conn.commit()
    conn.close()
    print("Registrasi berhasil.")

def autentikasi():
    conn = connect_db()
    cursor = conn.cursor()
    
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
    
    cursor.execute('SELECT * FROM laundry_options')
    laundry_options = cursor.fetchall()
    
    if not laundry_options:
        print("Tidak ada laundry tersedia.")
        conn.close()
        return
    
    print("Pilih laundry yang ingin diikuti:")
    for idx, option in enumerate(laundry_options, start=1):
        print(f"{idx}. {option[1]}")
    
    pilihan = int(input("Masukkan pilihan (nomor): "))
    
    if 1 <= pilihan <= len(laundry_options):
        laundry = laundry_options[pilihan - 1][1]
    else:
        print("Pilihan tidak valid.")
        conn.close()
        return
    
    cursor.execute('INSERT INTO subscriptions (username, laundry) VALUES (%s, %s)', (username, laundry))
    conn.commit()
    conn.close()
    print(f"{username} mengikuti {laundry}")

def kirim_pesanan(username):
    conn = connect_db()
    cursor = conn.cursor()
    
    berat_cucian = float(input("Masukkan berat cucian Anda (kg): "))
    jenis_laundry = input("Pilih jenis laundry (Hemat, Reguler, Ekspres): ")
    harga = hitung_harga(berat_cucian, jenis_laundry)
    estimasi = estimasi_waktu(jenis_laundry)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO orders (username, berat, jenis, harga, estimasi, timestamp) VALUES (%s, %s, %s, %s, %s, %s)', 
              (username, berat_cucian, jenis_laundry, harga, estimasi, timestamp))
    conn.commit()
    conn.close()
    return jenis_laundry, harga, estimasi

def hitung_harga(berat, jenis_laundry):
    if jenis_laundry.lower() == "hemat":
        return berat * 5000  # harga per kg untuk Hemat
    elif jenis_laundry.lower() == "reguler":
        return berat * 7000  # harga per kg untuk Reguler
    elif jenis_laundry.lower() == "ekspres":
        return berat * 10000  # harga per kg untuk Ekspres
    else:
        print("Jenis laundry tidak dikenal.")
        return None

def estimasi_waktu(jenis_laundry):
    if jenis_laundry.lower() == "hemat":
        return 3
    elif jenis_laundry.lower() == "reguler":
        return 2
    elif jenis_laundry.lower() == "ekspres":
        return 1
    else:
        print("Jenis laundry tidak dikenal.")
        return None

def pubLaundry():
    import paho.mqtt.client as mqtt
    import time

    conn = connect_db()
    cursor = conn.cursor()

    broker_address = "localhost"
    print("creating new instance")
    client = mqtt.Client(client_id="Laundry Service", protocol=mqtt.MQTTv311)
    print("connecting to broker")
    client.connect(broker_address, port=1883)

    client.loop_start()

    cursor.execute('SELECT * FROM orders')
    for order in cursor.fetchall():
        username = order[1]
        berat = order[2]
        jenis_laundry = order[3]
        harga = order[4]
        estimasi = order[5]
        timestamp = order[6]
        if estimasi:
            client.publish("laundry", f"Pengguna {username} memilih layanan {jenis_laundry} dengan berat cucian {berat} kg, harga {harga} IDR, dan estimasi waktu {estimasi} hari. Waktu pemesanan: {timestamp}.")
            print(f"Pesan dikirim: Pengguna {username} memilih layanan {jenis_laundry} dengan berat cucian {berat} kg, harga {harga} IDR, dan estimasi waktu {estimasi} hari. Waktu pemesanan: {timestamp}.")
    
    client.loop_stop()
    conn.close()

def main():
    start = input("Apakah klien sudah memiliki akun? (Y/n): ")
    if start.lower() == 'n':
        registrasi()
    username = None
    while not username:
        username = autentikasi()
    follow_laundry(username)
    jenis_laundry, harga, estimasi = kirim_pesanan(username)
    if estimasi:
        print(f"Estimasi waktu penyelesaian laundry: {estimasi} hari.")
        print(f"Harga total: {harga} IDR.")
    pubLaundry()

if __name__ == "__main__":
    main()
