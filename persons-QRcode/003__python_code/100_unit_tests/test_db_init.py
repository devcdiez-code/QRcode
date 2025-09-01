
# -------------------------------------------
#



import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_init import connect_db, check_table_exists, create_table_persons
import sqlite3
import pytest
import os

# Тестовая БД (отдельная, чтобы не ломать реальную)
TEST_DB_FILE = r"D:\persons-QRcode\_bd\test_persons_QRcode.db"

@pytest.fixture
def db_connection():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    conn = sqlite3.connect(TEST_DB_FILE)
    yield conn
    conn.close()
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_connect_db():
    conn = connect_db(TEST_DB_FILE)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_create_table_persons(db_connection):
    assert not check_table_exists(db_connection, "persons")
    create_table_persons(db_connection)
    assert check_table_exists(db_connection, "persons")

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
