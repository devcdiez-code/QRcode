import os
import shutil
import tkinter as tk
from init_pkg import db_init, db_utils
import sqlite3
#from init_pkg import db_init, db_utils


def run_form():
    root = tk.Tk()
    root.title("Добавить персону")

    # поля ввода
    tk.Label(root, text="Фамилия").grid(row=0, column=0)
    entry_last = tk.Entry(root)
    entry_last.grid(row=0, column=1)

    tk.Label(root, text="Имя").grid(row=1, column=0)
    entry_first = tk.Entry(root)
    entry_first.grid(row=1, column=1)

    tk.Label(root, text="Отчество").grid(row=2, column=0)
    entry_middle = tk.Entry(root)
    entry_middle.grid(row=2, column=1)

    tk.Label(root, text="Мобильный").grid(row=3, column=0)
    entry_mobile = tk.Entry(root)
    entry_mobile.grid(row=3, column=1)

    # кнопка выбора фото
    def choose_photo():
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите фото",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            print("Выбрано фото:", file_path)

    tk.Button(root, text="Загрузить фото", command=choose_photo).grid(row=4, column=0, columnspan=2)

    # кнопка сохранить
    def save_person():
        print("Сохраняем запись:")
        print(entry_last.get(), entry_first.get(), entry_middle.get(), entry_mobile.get())
        # тут будет вызов db_utils.save_person(...)

    tk.Button(root, text="Сохранить", command=save_person).grid(row=5, column=0, columnspan=2)

    root.mainloop()



def save_person_with_photo(first_name, middle_name, last_name, phone, photo_src):
    conn = db_utils.get_connection()
    cursor = conn.cursor()

    # вставляем запись без фото
    insert_sql = """
        INSERT INTO persons (
            first_name, middle_name, last_name, mobile1
        ) VALUES (?, ?, ?, ?)
    """
    cursor.execute(insert_sql, (first_name, middle_name, last_name, phone))
    person_id = cursor.lastrowid  # получаем ID новой записи

    # формируем имя файла
    safe_first = first_name or "noname"
    safe_middle = middle_name or ""
    safe_last = last_name or "nofam"
    file_name = f"{person_id}_{safe_first}_{safe_middle}_{safe_last}_1.jpg"
    dest_path = os.path.join(db_init.PHOTOS_PATH, file_name)

    # копируем фото
    shutil.copy(photo_src, dest_path)

    # обновляем запись с фото
    update_sql = """
        UPDATE persons
        SET photo_path = ?, photo_file = ?
        WHERE id = ?
    """
    cursor.execute(update_sql, (db_init.PHOTOS_PATH, file_name, person_id))

    conn.commit()
    conn.close()

    return person_id, file_name




if __name__ == "__main__":
    run_form()
