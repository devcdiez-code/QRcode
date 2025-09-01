import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os, random
from init_pkg import db_init, db_utils

PHOTO_FRAME_WIDTH = 15
PHOTO_FRAME_HEIGHT = 20

FORM_FRAME_WIDTH = 500
FORM_FRAME_HEIGHT = 550

ARCHIVE_DIR = r"D:\persons-QRcode\400__archive"


class PersonForm(tk.Tk):
    def __init__(self):
        super().__init__()
        geometry_str = f"{FORM_FRAME_WIDTH}x{FORM_FRAME_HEIGHT}"
        self.title(f"Добавить персону          {geometry_str}")
        self.geometry(geometry_str)
        self.resizable(True, True)

        # --- блок фото ---
        self.photo_label = tk.Label(
            self,
            text="Фото не загружено",
            width=PHOTO_FRAME_WIDTH,
            height=PHOTO_FRAME_HEIGHT,
            relief="sunken"
        )
        self.photo_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.btn_load_photo = tk.Button(self, text="Загрузить фото", command=self.load_photo)
        self.btn_load_photo.grid(row=5, column=0, columnspan=2, pady=5)

        self.photo_path = None
        self.photo_imgtk = None

        # --- поля ввода ---
        tk.Label(self, text="Фамилия:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_last = tk.Entry(self, width=40)
        self.entry_last.grid(row=0, column=1, pady=5)

        tk.Label(self, text="Имя:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_first = tk.Entry(self, width=40)
        self.entry_first.grid(row=1, column=1, pady=5)

        tk.Label(self, text="Отчество:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_middle = tk.Entry(self, width=40)
        self.entry_middle.grid(row=2, column=1, pady=5)

        tk.Label(self, text="Мобильный:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_mobile = tk.Entry(self, width=40)
        self.entry_mobile.grid(row=3, column=1, pady=5)

        # --- кнопки управления ---
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Сохранить", command=self.save).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.clear_form).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Выйти", command=self.quit).grid(row=0, column=2, padx=10)

        # --- статус-бар ---
        self.status_var = tk.StringVar()
        self.status_var.set(
            "Форма загружена. Горячие клавиши: Ctrl+S=Сохранить | Ctrl+O=Фото | Ctrl+N=Новая | Ctrl+Q=Выход"
        )
        self.status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bd=1, relief="sunken", anchor="w",
            fg="gray", font=("Arial", 9)
        )
        self.status_bar.grid(row=8, column=0, columnspan=2, sticky="we")

        # --- горячие клавиши ---
        self.bind("<Control-s>", lambda e: self.save())
        self.bind("<Control-o>", lambda e: self.load_photo())
        self.bind("<Control-n>", lambda e: self.clear_form())
        self.bind("<Control-q>", lambda e: self.quit())

        # --- загрузить случайное фото при старте ---
       # self.load_random_photo()

    def set_status(self, text, color="gray"):
        """Обновить статус-бар"""
        self.status_var.set(text)
        self.status_bar.config(fg=color)

    def load_random_photo(self):
        """Загрузить случайное фото из ARCHIVE_DIR"""
        if not os.path.isdir(ARCHIVE_DIR):
            self.set_status(f"Нет папки {ARCHIVE_DIR}", "red")
            return
        files = [f for f in os.listdir(ARCHIVE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not files:
            self.set_status("Нет фото в архиве", "red")
            return
        random_file = os.path.join(ARCHIVE_DIR, random.choice(files))
        self.show_photo(random_file)
        self.set_status(f"Загружено случайное фото: {os.path.basename(random_file)}", "green")

    def show_photo(self, path):
        """Отобразить фото в photo_label"""
        try:
            img = Image.open(path)

            # вписываем фото в рамку 200x150, сохраняя пропорции
            img.thumbnail((200, 150), Image.Resampling.LANCZOS)

            self.photo_imgtk = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.photo_imgtk, text="")
            self.photo_label.image = self.photo_imgtk
            self.photo_path = path
        except Exception as e:
            self.set_status(f"Ошибка загрузки фото: {e}", "red")

    def load_photo(self):
        """Загрузить фото с диска"""
        path = filedialog.askopenfilename(
            filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if not path:
            self.set_status("Загрузка фото отменена", "gray")
            return
        self.show_photo(path)
        self.set_status(f"Фото загружено: {os.path.basename(path)}", "green")

    def save(self):
        """Сохранение в БД + копия фото"""
        last = self.entry_last.get().strip().title()
        first = self.entry_first.get().strip().title()
        middle = self.entry_middle.get().strip().title()
        mobile = self.entry_mobile.get().strip()

        if not (last and first):
            messagebox.showerror("Ошибка", "Фамилия и Имя обязательны!")
            self.set_status("Ошибка: пустые Фамилия или Имя", "red")
            return

        try:
            # Сохраняем запись в БД
            person_id = db_utils.save_person(first, middle, last, mobile)

            # Фото — копируем с новым именем
            if self.photo_path:
                count = 1
                filename = f"{person_id}_{first}_{middle}_{last}_{count}.jpg"
                save_path = os.path.join(db_init.PHOTOS_DIR, filename)

                os.makedirs(db_init.PHOTOS_DIR, exist_ok=True)
                img = Image.open(self.photo_path)
                img.save(save_path)

                db_utils.update_person_photo(person_id, save_path, filename)

            messagebox.showinfo("Успех", f"Запись сохранена! ID={person_id}")
            self.set_status(f"Запись ID={person_id} сохранена", "green")
            self.clear_form()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.set_status(f"Ошибка: {e}", "red")

    def clear_form(self):
        """Очистить форму"""
        self.entry_last.delete(0, tk.END)
        self.entry_first.delete(0, tk.END)
        self.entry_middle.delete(0, tk.END)
        self.entry_mobile.delete(0, tk.END)
        self.photo_label.config(image="", text="Фото не загружено")
        self.photo_path = None
        self.set_status("Форма очищена. Готово к вводу новой записи", "gray")


if __name__ == "__main__":
    app = PersonForm()
    app.mainloop()
