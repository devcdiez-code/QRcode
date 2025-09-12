"""
db_utils.py
Версия: 1.2.0
Назначение: Работа с таблицей persons в SQLite-базе.
Описание:
 - подключение к БД
 - сохранение новой персоны
 - обновление фото
 - получение записи по ID
 - список персон
"""

import sqlite3
import os
from init_pkg import db_init

# Версия модуля
DB_UTILS_VERSION = "1.2.0"


def connect_db():
    """Соединение с БД"""
    return sqlite3.connect(db_init.DB_FILE)


def save_person(data):
    """Сохраняет запись в таблицу persons"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO persons (first_name, middle_name, last_name, mobile1, mobile2, mobile3, email, notes, photo_path, photo_file)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    person_id = cur.lastrowid
    conn.close()
    return person_id


def get_person(person_id):
    """Получает данные персоны по ID"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
    row = cur.fetchone()
    conn.close()
    return row
