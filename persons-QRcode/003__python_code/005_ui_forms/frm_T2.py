import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import random

from init_pkg import db_init, db_utils

FORM_FRAME_WIDTH = 700   # ширина окна увеличена, чтобы фото справа влезло
FORM_FRAME_HEIGHT = 400  # высота окна


class PersonForm(tk.Tk):
    def __init__(self):
        super().__init__()
        geometry_str = f"{FORM_FRAME_WIDTH}x{FORM_FRAME_HEIGHT}"
        self.title(f"Добавить персону          {geometry_str}")
        self.geometry(geometry_str)
        self.resizable(True, True)

        # --- поля ввода (слева) ---
        tk.Label(self, text="Фамилия:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_last = tk.Entry(self, width=30)
        self.entry_last.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(self, text="Имя:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_first = tk.Entry(self, width=30)
        self.entry_first.grid(row=1, column=1, pady=5, sticky="w")

        tk.Label(self, text="Отчество:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_middle = tk.Entry(self, width=30)
        self.entry_middle.grid(row=2, column=1, pady=5, sticky="w")

        tk.Label(self, text="Мобильный:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_mobile = tk.Entry(self, width=30)
        self.entry_mobile.grid(row=3, column=1, pady=5, sticky="w")

        # --- блок фото (справа) ---
        photo_frame = tk.Frame(self, relief="groove", bd=2, width=200, height=180)
        photo_frame.grid(row=0, column=2, rowspan=5, padx=15, pady=10, sticky="n")

        self.photo_label = tk.Label(photo_frame, text="Фото\nне загружено",
                                    width=200, height=150, bg="lightgray", anchor="center")
        self.photo_label.pack(padx=5, pady=5)

        self.btn_load_photo = tk.Button(photo_frame, text="Загрузить фото", command=self.load_photo)
        self.btn_load_photo.pack(pady=5)

        self.photo_path = None
        self.photo_imgtk = None

        # --- кнопки управления (снизу) ---
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=20)

        tk.Button(btn_frame, text="Сохранить", command=self.save).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.clear_form).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Выйти", command=self.quit).grid(row=0, column=2, padx=10)

        # загрузка случайного фото при старте
        self.load_random_photo(r"D:\persons-QRcode\400__archive")

        # горячие клавиши
        self.bind("<Control-s>", lambda e: self.save())
        self.bind("<Control-l>", lambda e: self.load_photo())
        self.bind("<Control-q>", lambda e: self.quit())

    def clear_form(self):
        """Очистить форму"""
        self.entry_last.delete(0, tk.END)
        self.entry_first.delete(0, tk.END)
        self.entry_middle.delete(0, tk.END)
        self.entry_mobile.delete(0, tk.END)
        self.photo_label.config(image="", text="Фото не загружено")
        self.photo_path = None

    def load_random_photo(self, folder_path):
        """Загрузить случайное фото из папки"""
        if not os.path.isdir(folder_path):
            return
        files = [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not files:
            return
        random_file = random.choice(files)
        path = os.path.join(folder_path, random_file)
        self.display_photo(path)

    def load_photo(self):
        """Загрузить фото с диска"""
        path = filedialog.askopenfilename(
            filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if path:
            self.display_photo(path)

    def display_photo(self, path):
        """Показать фото в photo_label с ресайзом до 200x150"""
        self.photo_path = path
        img = Image.open(path)
        img.thumbnail((200, 150))  # уменьшаем с сохранением пропорций
        self.photo_imgtk = ImageTk.PhotoImage(img)
        self.photo_label.config(image=self.photo_imgtk, text="")
        self.photo_label.image = self.photo_imgtk

    def save(self):
        """Сохранение в БД + копия фото"""
        last = self.entry_last.get().strip().title()
        first = self.entry_first.get().strip().title()
        middle = self.entry_middle.get().strip().title()
        mobile = self.entry_mobile.get().strip()

        if not (last and first):
            messagebox.showerror("Ошибка", "Фамилия и Имя обязательны!")
            return

        try:
            person_id = db_utils.save_person(first, middle, last, mobile)
            if self.photo_path:
                count = 1
                filename = f"{person_id}_{first}_{middle}_{last}_{count}.jpg"
                save_path = os.path.join(db_init.PHOTOS_DIR, filename)
                os.makedirs(db_init.PHOTOS_DIR, exist_ok=True)
                img = Image.open(self.photo_path)
                img.thumbnail((200, 150))
                img.save(save_path)
                db_utils.update_person_photo(person_id, save_path, filename)

            messagebox.showinfo("Успех", f"Запись сохранена! ID={person_id}")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    app = PersonForm()
    app.mainloop()
