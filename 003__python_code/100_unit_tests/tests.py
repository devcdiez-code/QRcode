import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import random

# === импорт путей из db_init.py ===
try:
    from db_init import PHOTO_DIR, DB_PATH
except ImportError:
    # запасной вариант
    DB_PATH = r"D:\persons-QRcode\_db\planB\persons_QRcode.db"
    PHOTO_DIR = r"D:\persons-QRcode\_photos"


# --- Проверка существования таблицы persons ---
def check_table_exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persons';")
    table = cursor.fetchone()
    conn.close()
    if not table:
        raise RuntimeError("❌ Таблица 'persons' не найдена в БД!")


# --- Генерация имени файла фото ---
def generate_photo_filename(person_id, first, middle, last):
    # Проверяем, сколько фото уже есть для этого id
    existing = [f for f in os.listdir(PHOTO_DIR) if f.startswith(f"{person_id}_")]
    cont = len(existing) + 1
    return f"{person_id}_{first}_{middle}_{last}_{cont}.jpg"


# --- Сохранение записи в БД ---
def save_person(first, middle, last, mobile, photo_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Вставляем запись с базовыми значениями
    sql_insert = """
    INSERT INTO persons (first_name, middle_name, last_name, mobile1, gender, language, active)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        first, middle, last, mobile,
        random.choice(["мужской", "женский", ""]),
        "ru",
        True
    )

    cursor.execute(sql_insert, values)
    person_id = cursor.lastrowid  # получаем ID записи

    # Если выбрано фото → копируем в PHOTO_DIR
    if photo_path:
        if not os.path.exists(PHOTO_DIR):
            os.makedirs(PHOTO_DIR)

        filename = generate_photo_filename(person_id, first, middle, last)
        dest_path = os.path.join(PHOTO_DIR, filename)
        shutil.copy(photo_path, dest_path)

        # Обновляем путь к фото в БД
        cursor.execute("UPDATE persons SET photo_path=? WHERE id=?", (dest_path, person_id))

    conn.commit()
    conn.close()
    messagebox.showinfo("Успех", f"✅ Запись добавлена! ID={person_id}")


# --- Форма tkinter ---
def run_form():
    check_table_exists()

    root = tk.Tk()
    root.title("Добавление записи в persons")
    root.geometry("400x300")

    tk.Label(root, text="Фамилия").pack()
    entry_last = tk.Entry(root)
    entry_last.pack()

    tk.Label(root, text="Имя").pack()
    entry_first = tk.Entry(root)
    entry_first.pack()

    tk.Label(root, text="Отчество").pack()
    entry_middle = tk.Entry(root)
    entry_middle.pack()

    tk.Label(root, text="Мобильный").pack()
    entry_mobile = tk.Entry(root)
    entry_mobile.pack()

    photo_path = {"file": None}

    def choose_photo():
        file = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg;*.jpeg;*.png")])
        if file:
            photo_path["file"] = file
            messagebox.showinfo("Фото выбрано", file)

    def submit():
        try:
            save_person(
                entry_first.get(),
                entry_middle.get(),
                entry_last.get(),
                entry_mobile.get(),
                photo_path["file"]
            )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(root, text="Выбрать фото", command=choose_photo).pack(pady=5)
    tk.Button(root, text="Сохранить", command=submit).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    run_form()
