"""
db_init.py
Версия: 1.0.0
Назначение: Инициализация путей и параметров базы данных.
Описание:
 - хранит путь к файлу БД
 - хранит путь для фотографий
 - хранит путь для логов
"""

import os

# Версия модуля
DB_INIT_VERSION = "1.0.0"

# Базовый путь проекта (корень)
BASE_DIR = r"D:\persons-QRcode"

# Путь к файлу БД
DB_FILE = os.path.join(BASE_DIR, "_db", "persons_QRcode.db")

# Путь для хранения фотографий
PHOTOS_DIR = os.path.join(BASE_DIR, "_photos")

# Папка для логов
LOGS_DIR = os.path.join(BASE_DIR, "_db", "_logs")

# Создание папок при необходимости
os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
