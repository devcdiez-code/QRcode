import sys
import os
import sqlite3
import pytest
import pandas as pd
import qrcode
import warnings

# --- Подключение проекта ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_init import connect_db, check_table_exists, create_table_persons, SQL_CREATE_PERSONS

# --- Путь для тестовой БД ---
TEST_DB_FILE = r"D:\persons-QRcode\_bd\test_persons_QRcode.db"

# --- Игнорирование UserWarning от pkg_resources ---
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

# -------------------------------
# Fixture: соединение с тестовой БД
# -------------------------------
@pytest.fixture
def db_connection():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    conn = sqlite3.connect(TEST_DB_FILE)
    yield conn
    conn.close()
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

# -------------------------------
# 1. Тест создания таблицы
# -------------------------------
def test_create_table_persons(db_connection):
    create_table_persons(db_connection)
    assert check_table_exists(db_connection, "persons")

# -------------------------------
# 2. Тест вставки записи с полным набором полей
# -------------------------------
def test_insert_full_record(db_connection):
    create_table_persons(db_connection)
    cursor = db_connection.cursor()

    record = {
        "first_name": "Людовик",
        "middle_name": "",
        "last_name": "Бетховен",
        "last_name2": "",
        "gender": "мужской",
        "salutation": "",
        "language": "немецкий",
        "status": "",
        "organization": "",
        "position": "композитор",
        "mobile1": "+491512345678",
        "mobile2": "",
        "mobile3": "",
        "mobile4": "",
        "email": "beethoven_l@example.com",
        "email_confirmed": 0,
        "contact_first_name": "",
        "contact_middle_name": "",
        "contact_last_name": "",
        "contact_last_name2": "",
        "contact_gender": "",
        "contact_language": "",
        "contact_position": "",
        "contact_mobile1": "",
        "contact_mobile2": "",
        "contact_mobile3": "",
        "contact_mobile4": "",
        "contact_email": "",
        "contact_email_confirmed": 0,
        "qr_code": "",
        "qr_created": "",
        "badge_created": 0,
        "badge_created_at": "",
        "active": 1,
        "allowed": 1,
        "notified_email": 0,
        "notified_email_at": "",
        "notified_whatsapp": 0,
        "notified_whatsapp_at": "",
        "notified_telegram": 0,
        "notified_telegram_at": "",
        "notified_max": 0,
        "notified_max_at": "",
        "passed": 0,
        "passed_at": "",
        "gate_number": "",
        "notes": "Лунная соната",
        "title": "",
        "photo_path": "1_Бетховен_Людовик_.jpg"
    }

    cols = ", ".join(record.keys())
    placeholders = ", ".join("?" for _ in record)
    cursor.execute(f"INSERT INTO persons ({cols}) VALUES ({placeholders})", tuple(record.values()))
    db_connection.commit()

    cursor.execute("SELECT first_name, last_name, position, notes FROM persons WHERE first_name='Людовик'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "Людовик"
    assert row[2] == "композитор"
    assert row[3] == "Лунная соната"

# -------------------------------
# 3. Тест импорта CSV с полными данными
# -------------------------------
def test_import_csv_full(db_connection, tmp_path):
    create_table_persons(db_connection)
    csv_file = tmp_path / "persons_full.csv"

    # создаём CSV с 2-3 тестовыми реальными персонами
    df = pd.DataFrame([
        {
            "first_name": "Брэд",
            "middle_name": "",
            "last_name": "Питт",
            "last_name2": "",
            "gender": "мужской",
            "salutation": "",
            "language": "английский",
            "status": "",
            "organization": "",
            "position": "актёр",
            "mobile1": "+12025550123",
            "mobile2": "",
            "mobile3": "",
            "mobile4": "",
            "email": "pitt_b@example.com",
            "email_confirmed": 0,
            "contact_first_name": "",
            "contact_middle_name": "",
            "contact_last_name": "",
            "contact_last_name2": "",
            "contact_gender": "",
            "contact_language": "",
            "contact_position": "",
            "contact_mobile1": "",
            "contact_mobile2": "",
            "contact_mobile3": "",
            "contact_mobile4": "",
            "contact_email": "",
            "contact_email_confirmed": 0,
            "qr_code": "",
            "qr_created": "",
            "badge_created": 0,
            "badge_created_at": "",
            "active": 1,
            "allowed": 1,
            "notified_email": 0,
            "notified_email_at": "",
            "notified_whatsapp": 0,
            "notified_whatsapp_at": "",
            "notified_telegram": 0,
            "notified_telegram_at": "",
            "notified_max": 0,
            "notified_max_at": "",
            "passed": 0,
            "passed_at": "",
            "gate_number": "",
            "notes": "Фильм «Бойцовский клуб»",
            "title": "",
            "photo_path": "2_Питт_Брэд_.jpg"
        }
    ])
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

    df_loaded = pd.read_csv(csv_file, encoding="utf-8-sig")
    df_loaded.to_sql("persons", db_connection, if_exists="append", index=False)

    cursor = db_connection.cursor()
    cursor.execute("SELECT first_name, last_name, position, notes FROM persons WHERE first_name='Брэд'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "Брэд"
    assert row[2] == "актёр"
    assert row[3] == "Фильм «Бойцовский клуб»"

# -------------------------------
# 4. Тест генерации QR-кодов для всех записей
# -------------------------------
def test_generate_qr_all(db_connection, tmp_path):
    create_table_persons(db_connection)
    cursor = db_connection.cursor()

    # добавляем 2 записи
    people = [
        (1, "Людовик", "Бетховен", "композитор", "", "+491512345678", "beethoven_l@example.com"),
        (2, "Брэд", "Питт", "актёр", "ТестОрг", "+12025550123", "pitt_b@example.com")
    ]
    cursor.executemany("""
        INSERT INTO persons (id, first_name, last_name, position, organization, mobile1, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, people)
    db_connection.commit()

    # генерируем QR
    cursor.execute("SELECT id, first_name, last_name, position, organization, mobile1, email FROM persons")
    rows = cursor.fetchall()
    for row in rows:
        payload = {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "position": row[3],
            "organization": row[4],
            "mobile": row[5],
            "email": row[6],
        }
        img = qrcode.make(str(payload))
        qr_file = tmp_path / f"{row[0]}_qr.png"
        img.save(qr_file)
        assert qr_file.exists()
