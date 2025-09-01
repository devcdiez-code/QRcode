import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import shutil
import qrcode
from datetime import datetime

# Пути
DB_PATH = r"D:\persons-QRcode\_bd\persons_QRcode.db"
PHOTO_DIR = r"D:\persons-QRcode\_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# Подключение к БД
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Создание таблицы, если нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    last_name2 TEXT,
    gender TEXT CHECK(gender IN ('мужской','женский')) NOT NULL,
    salutation TEXT,
    language TEXT,
    status TEXT CHECK(status IN ('гость','сопровождающий')),
    organization TEXT,
    position TEXT,
    mobile1 TEXT,
    mobile2 TEXT,
    mobile3 TEXT,
    mobile4 TEXT,
    email TEXT,
    email_confirmed BOOLEAN DEFAULT 0,
    contact_first_name TEXT,
    contact_middle_name TEXT,
    contact_last_name TEXT,
    contact_last_name2 TEXT,
    contact_gender TEXT CHECK(contact_gender IN ('мужской','женский')),
    contact_language TEXT,
    contact_position TEXT,
    contact_mobile1 TEXT,
    contact_mobile2 TEXT,
    contact_mobile3 TEXT,
    contact_mobile4 TEXT,
    contact_email TEXT,
    contact_email_confirmed BOOLEAN DEFAULT 0,
    qr_code TEXT UNIQUE,
    badge_created_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    is_allowed BOOLEAN DEFAULT 1,
    notified_email BOOLEAN DEFAULT 0,
    notified_email_time DATETIME,
    notified_whatsapp BOOLEAN DEFAULT 0,
    notified_whatsapp_time DATETIME,
    notified_telegram BOOLEAN DEFAULT 0,
    notified_telegram_time DATETIME,
    notified_max BOOLEAN DEFAULT 0,
    notified_max_time DATETIME,
    passed BOOLEAN DEFAULT 0,
    passed_time DATETIME,
    gate_number TEXT,
    note TEXT,
    photo_path TEXT
);
""")
conn.commit()

# --- GUI ---
root = tk.Tk()
root.title("Управление гостями (QRcode)")
root.geometry("1200x800")

fields = {}
form_fields = [
    ("Имя", "first_name"),
    ("Отчество", "middle_name"),
    ("Фамилия", "last_name"),
    ("Фамилия 2", "last_name2"),
    ("Пол", "gender"),
    ("Обращение", "salutation"),
    ("Язык", "language"),
    ("Статус", "status"),
    ("Организация", "organization"),
    ("Должность", "position"),
    ("Мобильный 1", "mobile1"),
    ("Мобильный 2", "mobile2"),
    ("Мобильный 3", "mobile3"),
    ("Мобильный 4", "mobile4"),
    ("Email", "email"),
    ("Email подтвержден", "email_confirmed"),
    ("Имя контакта", "contact_first_name"),
    ("Отчество контакта", "contact_middle_name"),
    ("Фамилия контакта", "contact_last_name"),
    ("Фамилия 2 контакта", "contact_last_name2"),
    ("Пол контакта", "contact_gender"),
    ("Язык контакта", "contact_language"),
    ("Должность контакта", "contact_position"),
    ("Телефон 1 контакта", "contact_mobile1"),
    ("Телефон 2 контакта", "contact_mobile2"),
    ("Телефон 3 контакта", "contact_mobile3"),
    ("Телефон 4 контакта", "contact_mobile4"),
    ("Email контакта", "contact_email"),
    ("Email контакт подтвержден", "contact_email_confirmed"),
    ("Примечание", "note")
]

row = 0
for label, key in form_fields:
    tk.Label(root, text=label).grid(row=row, column=0, sticky="w")
    if "пол" in label.lower():
        combo = ttk.Combobox(root, values=["мужской", "женский"])
        combo.grid(row=row, column=1, sticky="ew")
        fields[key] = combo
    elif "подтвержден" in label.lower():
        var = tk.BooleanVar()
        tk.Checkbutton(root, variable=var).grid(row=row, column=1, sticky="w")
        fields[key] = var
    else:
        entry = tk.Entry(root)
        entry.grid(row=row, column=1, sticky="ew")
        fields[key] = entry
    row += 1

photo_path = tk.StringVar()
def choose_photo():
    file = filedialog.askopenfilename(filetypes=[("JPEG", "*.jpg")])
    if file:
        fname = os.path.basename(file)
        dest = os.path.join(PHOTO_DIR, fname)
        shutil.copy(file, dest)
        photo_path.set(dest)
        messagebox.showinfo("Фото", f"Фото сохранено: {dest}")

tk.Button(root, text="Выбрать фото", command=choose_photo).grid(row=row-1, column=2)

qr_code_value = tk.StringVar()
def generate_qr():
    data = fields["first_name"].get() + "_" + fields["last_name"].get()
    img = qrcode.make(data)
    qr_filename = os.path.join(PHOTO_DIR, f"qr_{data}.png")
    img.save(qr_filename)
    qr_code_value.set(qr_filename)
    messagebox.showinfo("QR", f"QR-код сохранен: {qr_filename}")

 tk.Button(root, text="Сгенерировать QR", command=generate_qr).grid(row=row, column=0)

# Treeview для списка записей
tree = ttk.Treeview(root, columns=("ID", "ФИО", "Телефон", "Email", "Статус", "Язык"), show="headings")
tree.heading("ID", text="ID")
tree.heading("ФИО", text="ФИО")
tree.heading("Телефон", text="Телефон")
tree.heading("Email", text="Email")
tree.heading("Статус", text="Статус")
tree.heading("Язык", text="Язык")
tree.grid(row=row+1, column=0, columnspan=4, sticky="nsew")
root.grid_rowconfigure(row+1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Функции работы с БД
def refresh_tree():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT id, first_name || ' ' || middle_name || ' ' || last_name, mobile1, email, status, language FROM persons")
    for row_data in cursor.fetchall():
        tree.insert('', tk.END, values=row_data)

def save_to_db():
    values = {}
    for label, key in form_fields:
        if isinstance(fields[key], tk.Entry):
            values[key] = fields[key].get()
        elif isinstance(fields[key], ttk.Combobox):
            values[key] = fields[key].get()
        elif isinstance(fields[key], tk.BooleanVar):
            values[key] = int(fields[key].get())

    values["photo_path"] = photo_path.get()
    values["qr_code"] = qr_code_value.get()
    values["badge_created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    columns = ", ".join(values.keys())
    placeholders = ", ".join(["?" for _ in values])

    cursor.execute(f"INSERT INTO persons ({columns}) VALUES ({placeholders})", list(values.values()))
    conn.commit()
    refresh_tree()
    messagebox.showinfo("Успех", "Запись добавлена")

# Кнопка добавить
 tk.Button(root, text="Добавить запись", command=save_to_db).grid(row=row+2, column=0)

refresh_tree()
root.mainloop()
