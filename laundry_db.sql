CREATE DATABASE laundry_db;

USE laundry_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    laundry VARCHAR(255)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    berat FLOAT,
    jenis VARCHAR(255),
    harga FLOAT,
    estimasi INT
);