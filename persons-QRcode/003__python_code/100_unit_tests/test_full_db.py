import sys
import os
import sqlite3
import pytest
import pandas as pd
import qrcode
import warnings

# --- Подключение проекта ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_init import connect_db, check_table_exists, create_table_persons

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
# 1. Тест подключения к БД
# -------------------------------
def test_connect_db():
    conn = connect_db(TEST_DB_FILE)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

# -------------------------------
# 2. Тест создания таблицы
# -------------------------------
def test_create_table_persons(db_connection):
    assert not check_table_exists(db_connection, "persons")
    create_table_persons(db_connection)
    assert check_table_exists(db_connection, "persons")

# -------------------------------
# 3. Тест вставки и выборки данных
# -------------------------------
def test_insert_and_select(db_connection):
    create_table_persons(db_connection)
    cursor = db_connection.cursor()
    cursor.execute("""
        INSERT INTO persons (first_name, last_name, gender)
        VALUES (?, ?, ?)
    """, ("Тест", "Юнит", "мужской"))
    db_connection.commit()
    cursor.execute("SELECT first_name, last_name, gender FROM persons WHERE first_name=?", ("Тест",))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "Тест"
    assert row[1] == "Юнит"
    assert row[2] == "мужской"

# -------------------------------
# 4. Тест ограничения CHECK(gender IN ...)
# -------------------------------
def test_gender_check_constraint(db_connection):
    create_table_persons(db_connection)
    cursor = db_connection.cursor()
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO persons (first_name, last_name, gender)
            VALUES (?, ?, ?)
        """, ("Проверка", "Неверно", "неизвестно"))
        db_connection.commit()

# -------------------------------
# 5. Тест импорта CSV
# -------------------------------
def test_import_csv(db_connection, tmp_path):
    create_table_persons(db_connection)
    # создаём временный CSV
    csv_file = tmp_path / "test_persons.csv"
    df = pd.DataFrame([{
        "first_name": "Алексей",
        "middle_name": "",
        "last_name": "Иванов",
        "gender": "мужской",
        "email": "ivanov_a@example.com",
        "contact_gender": "мужской",
        "position": "актёр",
        "notes": "Известный фильм",
        "photo_path": "1_Иванов_Алексей_.jpg"
    }])
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

    # импорт CSV
    df_loaded = pd.read_csv(csv_file, encoding="utf-8-sig")
    df_loaded.to_sql("persons", db_connection, if_exists="append", index=False)

    # проверка
    cursor = db_connection.cursor()
    cursor.execute("SELECT first_name, last_name FROM persons WHERE first_name='Алексей'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "Алексей"
    assert row[1] == "Иванов"

# -------------------------------
# 6. Тест генерации QR-кода
# -------------------------------
def test_generate_qr(db_connection, tmp_path):
    create_table_persons(db_connection)
    cursor = db_connection.cursor()
    cursor.execute("""
        INSERT INTO persons (id, first_name, last_name, position, organization, mobile1, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, "Тест", "QR", "актёр", "ТестОрг", "+79000000000", "test_qr@example.com"))
    db_connection.commit()

    # генерация QR
    cursor.execute("SELECT id, first_name, last_name, position, organization, mobile1, email FROM persons")
    row = cursor.fetchone()
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
    qr_file = tmp_path / "1_qr.png"
    img.save(qr_file)
    assert qr_file.exists()
