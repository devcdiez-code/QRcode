import os
import shutil
import sqlite3
from init_pkg import db_init


def get_connection():
    return sqlite3.connect(db_init.DB_FILE)


def save_person(first_name, middle_name, last_name, mobile, photo_path=None):
    """
    Сохраняем персону в БД, копируем фото в папку PHOTO_DIR.
    Имя фото = id_name1_name2_name3_count.jpg
    """
    conn = get_connection()
    cur = conn.cursor()

    # Вставляем запись (сначала без фото)
    cur.execute("""
        INSERT INTO persons (first_name, middle_name, last_name, mobile1)
        VALUES (?, ?, ?, ?)
    """, (first_name, middle_name, last_name, mobile))
    conn.commit()

    # Получаем id
    person_id = cur.lastrowid

    saved_photo_filename = None
    if photo_path:
        os.makedirs(db_init.PHOTO_DIR, exist_ok=True)

        # считаем сколько уже фото у этой персоны
        cur.execute("SELECT COUNT(*) FROM persons WHERE id = ?", (person_id,))
        count = 1  # пока делаем только одно фото

        # формируем имя файла
        ext = os.path.splitext(photo_path)[1].lower()
        saved_photo_filename = f"{person_id}_{first_name}_{middle_name}_{last_name}_{count}{ext}"
        saved_photo_filename = saved_photo_filename.replace(" ", "_").replace("-", "_")

        dest_path = os.path.join(db_init.PHOTO_DIR, saved_photo_filename)
        shutil.copy2(photo_path, dest_path)

        # обновляем запись в БД
        cur.execute("""
            UPDATE persons
            SET photo_path = ?, photo_file = ?
            WHERE id = ?
        """, (db_init.PHOTO_DIR, saved_photo_filename, person_id))
        conn.commit()

    conn.close()
    return person_id, saved_photo_filename


def update_person_photo(person_id, photo_path, photo_file):
    """Обновляет фото у персоны"""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE persons SET photo_path=?, photo_file=? WHERE id=?",
        (photo_path, photo_file, person_id)
    )
    conn.commit()
    conn.close()

