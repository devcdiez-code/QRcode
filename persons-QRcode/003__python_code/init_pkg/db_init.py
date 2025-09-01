import sqlite3
import logging
import os
import sys

# -----------------------------
# Главные пути проекта
# -----------------------------
BASE_DIR = r"D:\persons-QRcode"           # корневая папка проекта
DATA_DIR = os.path.join(BASE_DIR, "_db")  # база данных DB, CSV
LOG_DIR = os.path.join(BASE_DIR, "_logs")      # логи
PHOTO_DIR = os.path.join(BASE_DIR, "_photos")  # фотографии

# создаём папки, если их нет
for path in [DATA_DIR, PHOTO_DIR, LOG_DIR]:
    os.makedirs(path, exist_ok=True)

# -----------------------------
# Пути к файлам

DB_FILE = os.path.join(DATA_DIR, "persons_QRcode.db")
LOG_FILE = os.path.join(LOG_DIR, "db_init.log")
CSV_FILE = os.path.join(DATA_DIR, "persons_full.csv")

# -----------------------------
#  table таблица
TABLE_NAME = "persons"

# -------------------------------------------------------------------------------------
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)  # также вывод в консоль
    ]
)

logger = logging.getLogger("db_init_logger")
# -------------------------------------------------------------------------------------


# SQL для создания таблицы
SQL_CREATE_PERSONS = """
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT, -- имя персоны
    middle_name TEXT,  -- patronimic отчество персоны
    last_name TEXT,  -- surname фамилия 
    last_name2 TEXT, -- другая фамилия персоны
    gender TEXT CHECK(gender IN ('мужской','женский','')),
    salutation TEXT,
    language TEXT, -- язык общения с персоной
    status TEXT,
    organization TEXT, -- наименование организации персоны
    position TEXT,     -- должность персоны
    mobile1 TEXT,      -- номер мобильного телефона 1 персоны
    mobile2 TEXT,
    mobile3 TEXT,
    mobile4 TEXT,
    email TEXT UNIQUE,  -- электронная почта персоны
    email_confirmed BOOLEAN, -- электронная почта персоны подтверждена
    contact_first_name TEXT,  --  имя контактного лица
    contact_middle_name TEXT,  -- patronimic отчество контактного лица
    contact_last_name TEXT,
    contact_last_name2 TEXT,
    contact_gender TEXT CHECK(contact_gender IN ('мужской','женский','')),
    contact_language TEXT,
    contact_position TEXT,
    contact_mobile1 TEXT,
    contact_mobile2 TEXT,
    contact_mobile3 TEXT,
    contact_mobile4 TEXT,
    contact_email TEXT UNIQUE, -- почта контактного лица
    contact_email_confirmed BOOLEAN,
    qr_code TEXT,
    qr_created TEXT,  -- дата и время создания QR кода
    badge_created BOOLEAN,   -- дата и время создания бэйджа
    badge_created_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- -- дата и время создания записи
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN,   -- запись активна
    allowed BOOLEAN,  -- вход персоны разрешён
    notified_email BOOLEAN,  -- приглашение отправлено по e-mail
    notified_email_at TIMESTAMP,
    notified_whatsapp BOOLEAN, -- -- приглашение отправлено
    notified_whatsapp_at TIMESTAMP,
    notified_telegram BOOLEAN, -- приглашение отправлено
    notified_telegram_at TIMESTAMP,
    notified_max BOOLEAN, -- -- приглашение отправлено
    notified_max_at TIMESTAMP,
    passed BOOLEAN,   --  персона на мероприятие прошла 
    passed_at TIMESTAMP, -- время прохода персоны 
    gate_number TEXT,  -- номер или наименование входа
    notes TEXT,   -- заметки
    title TEXT,
    photo_path TEXT,
    photo_file TEXT -- файл фото 
);
"""

# -------------------------------
# 1. Подключение
# -------------------------------

# Подключение к базе (если файла нет, SQLite создаст его автоматически)
def connect_db(db_file=DB_FILE):
    try:
        conn = sqlite3.connect(db_file)
        logger.info(f"Успешное подключение к БД: {db_file}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise

# -------------------------------
# 2. Проверка существования таблицы
# -------------------------------
def check_table_exists(conn, table_name="persons") -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone() is not None
        logger.info(f"Таблица '{table_name}' существует: {exists}")
        return exists
    except sqlite3.Error as e:
        logger.error(f"Ошибка при проверке таблицы {table_name}: {e}")
        return False

# -------------------------------
# 3. Создание таблицы
# -------------------------------
def create_table_persons(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(SQL_CREATE_PERSONS)
        conn.commit()
        logger.info("Таблица persons создана или уже существовала.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы persons: {e}")
        raise

# -------------------------------
# 4. Инициализация БД
# -------------------------------
def init_db(db_file=DB_FILE):
    conn = connect_db(db_file)
    if not check_table_exists(conn, "persons"):
        create_table_persons(conn)
    conn.close()
    logger.info("Инициализация БД завершена.")
    # принудительный flush лога
    for handler in logger.handlers:
        handler.flush()
    print("✅ Инициализация БД завершена. Логи см. в", LOG_FILE)


# -------------------------------
# Тестовый запуск
# -------------------------------
if __name__ == "__main__":
    init_db()
