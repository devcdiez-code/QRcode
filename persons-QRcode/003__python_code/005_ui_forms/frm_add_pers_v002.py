
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
import sqlite3
import logging

from init_pkg import db_init

# --- Логирование ---
os.makedirs(db_init.LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=db_init.LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Проверка таблицы ---
def check_table_exists():
    if not os.path.exists(db_init.DB_FILE):
        raise RuntimeError("❌ Файл БД не найден!")
    conn = sqlite3.connect(db_init.DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (db_init.TABLE_NAME,)
    )
    if cur.fetchone() is None:
        raise RuntimeError(f"❌ Таблица '{db_init.TABLE_NAME}' не найдена в БД!")
    conn.close()

# --- Сохранение записи ---
def save_person(fname, mname, lname, phone, photo_path):
    conn = sqlite3.connect(db_init.DB_FILE)
    cur = conn.cursor()

    # Вставляем запись
    cur.execute(f"""
        INSERT INTO {db_init.TABLE_NAME} 
        (first_name, middle_name, last_name, mobile1) 
        VALUES (?, ?, ?, ?)
    """, (fname, mname, lname, phone))
    person_id = cur.lastrowid
    conn.commit()

    # Генерация имени файла фото
    count = 1  # счётчик файлов
    filename = f"{person_id}_{fname}_{mname}_{lname}_{count}.jpg"
    dest_path = os.path.join(db_init.PHOTO_DIR, filename)

    os.makedirs(db_init.PHOTO_DIR, exist_ok=True)
    shutil.copy(photo_path, dest_path)

    logging.info(f"Добавлена запись id={person_id}, фото={filename}")
    conn.close()
    return person_id, dest_path

# --- GUI ---
def run_form():
    def submit():
        fname = entry_fname.get()
        mname = entry_mname.get()
        lname = entry_lname.get()
        phone = entry_phone.get()
        photo = photo_path_var.get()

        if not fname or not lname or not phone or not photo:
            messagebox.showerror("Ошибка", "Заполните все поля и выберите фото!")
            return

        try:
            pid, saved = save_person(fname, mname, lname, phone, photo)
            messagebox.showinfo("Успех", f"Запись {pid} сохранена\nФото: {saved}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении: {e}")
            messagebox.showerror("Ошибка", str(e))

    def select_photo():
        file = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg;*.jpeg")])
        if file:
            photo_path_var.set(file)

    root = tk.Tk()
    root.geometry("400x250+200+100")
    root.title("Добавление персоны")

    tk.Label(root, text="Имя:").grid(row=0, column=0, sticky="e")
    entry_fname = tk.Entry(root); entry_fname.grid(row=0, column=1)

    tk.Label(root, text="Отчество:").grid(row=1, column=0, sticky="e")
    entry_mname = tk.Entry(root); entry_mname.grid(row=1, column=1)

    tk.Label(root, text="Фамилия:").grid(row=2, column=0, sticky="e")
    entry_lname = tk.Entry(root); entry_lname.grid(row=2, column=1)

    tk.Label(root, text="Телефон:").grid(row=3, column=0, sticky="e")
    entry_phone = tk.Entry(root); entry_phone.grid(row=3, column=1)

    tk.Button(root, text="Выбрать фото", command=select_photo).grid(row=4, column=0)
    photo_path_var = tk.StringVar()
    tk.Entry(root, textvariable=photo_path_var, state="readonly", width=40).grid(row=4, column=1)

    tk.Button(root, text="Сохранить", command=submit).grid(row=5, column=0, columnspan=2)

    check_table_exists()
    root.mainloop()


if __name__ == "__main__":
    run_form()