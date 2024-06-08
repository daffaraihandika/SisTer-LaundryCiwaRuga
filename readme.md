# Optimalisasi Layanan Laundry Melalui Sistem Terdistribusi Berbasis Publish-Subscribe dan Arsitektur Client-Server

## Deskripsi Proyek
Proyek ini bertujuan untuk mengembangkan sistem laundry terdistribusi yang melibatkan dua penyedia layanan: "Laundry Ciwa" dan "Laundry Ruga". Sistem ini dirancang untuk memfasilitasi komunikasi yang efektif antara kedua laundry dengan kliennya, serta mengelola pesanan dan memberikan informasi mengenai estimasi waktu penjemputan baju kotor dan pengantaran baju bersih berdasarkan jenis paket laundry (hemat, reguler, dan ekspres).

## Fitur Utama
- Klien dapat memilih untuk mengikuti salah satu atau kedua laundry.
- Klien menerima pembaruan estimasi waktu penjemputan dan pengantaran.
- Perbandingan waktu penyelesaian layanan antara Laundry Ciwa dan Laundry Ruga.

## Struktur Proyek
###### ├── main.py
###### ├── client.py
###### ├── README.md
###### └── requirements.txt


## Instalasi Dependency
Pastikan Anda memiliki `mysql-connector-python` dan `paho-mqtt` yang terdaftar dalam `requirements.txt`. Instalasi dapat dilakukan dengan:
```
pip install -r requirements.txt
```


## Konfigurasi database
Konfigurasikan database MySQL dengan membuat tabel-tabel berikut:
```sql
CREATE DATABASE laundry_db;

USE laundry_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL  
);

CREATE TABLE subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    laundry VARCHAR(255) NOT NULL
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    berat FLOAT NOT NULL,
    jenis VARCHAR(255) NOT NULL,
    harga FLOAT NOT NULL,
    estimasi INT NOT NULL,
    timestamp DATETIME NOT NULL,
    laundry VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL
);

CREATE TABLE laundry_options (
  id int(11) NOT NULL,
  name varchar(255) NOT NULL,
  hemat int(11) NOT NULL,
  reguler int(11) NOT NULL,
  ekspres int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


INSERT INTO laundry_options (name, hemat, reguler, ekspres) VALUES
('Laundry Ciwa', 3, 2, 1),
('Laundry Ruga', 4, 3, 2);
```

# Langkah-Langkah Instalasi dan Konfigurasi Mosquitto

1. **Pastikan Mosquitto Sudah Terinstal pada Device**
   
   Pertama, pastikan Mosquitto sudah terinstal pada device Anda. Jika belum, Anda dapat mengunduh dan menginstalnya dari situs resmi Mosquitto.

2. **Arahkan ke Direktori Mosquitto**

   Buka File Explorer, lalu arahkan ke direktori: `C:\Program Files\mosquitto`


3. **Buka File Konfigurasi dengan VSCode**

Kemudian, buka file `mosquitto.conf` dengan Visual Studio Code (VSCode).

4. **Tambahkan Baris Konfigurasi**

Tambahkan kedua baris konfigurasi berikut ke dalam file `mosquitto.conf`:

```plaintext
listener 1883 0.0.0.0
allow_anonymous true
```
   
## Menjalankan Broker MQTT

Langkah pertama adalah menjalankan `mosquitto`. Buka CMD dengan "run as administrator", kemudian masukkan perintah berikut:
```bash
mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf" -v
```


### Menjalankan Main Application (Publisher)

1. Buka terminal, lalu arahkan ke direktori aplikasi.
2. Jalankan perintah berikut:
    ```bash
    python main.py
    ```
3. Input nama laundry (Laundry Ciwa atau Laundry Ruga) dan tekan Enter.
4. Sistem akan menampilkan pesan:
    ```
    Masukkan aksi untuk Laundry <nama>:
    ```
5. Ketik `proses` untuk memproses pesanan baru atau `keluar` untuk keluar.

### Menjalankan Client Application (Subscriber)

1. Buka terminal, lalu arahkan ke direktori aplikasi.
2. Jalankan perintah berikut:
    ```bash
    python client.py
    ```
3. Jika belum memiliki akun, input `n` dan ikuti langkah registrasi.
4. Jika sudah memiliki akun, input `y` dan ikuti langkah autentikasi.
5. Sistem akan menampilkan daftar laundry yang belum diikuti, pilih laundry yang ingin diikuti.
6. Input berat cucian dan jenis laundry (hemat, reguler, atau ekspres).
7. Sistem akan menampilkan estimasi waktu selesai dan harga, serta mengirimkan pesanan.




