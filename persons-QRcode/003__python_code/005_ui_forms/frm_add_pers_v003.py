import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from init_pkg import db_utils


class PersonForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Добавление персоны")
        self.geometry("400x500")  # компактный размер

        # Переменные
        self.first_name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.mobile_var = tk.StringVar()
        self.photo_path = None

        # Форма
        tk.Label(self, text="Имя:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(self, textvariable=self.first_name_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Отчество:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(self, textvariable=self.middle_name_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Фамилия:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(self, textvariable=self.last_name_var).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="Мобильный:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(self, textvariable=self.mobile_var).grid(row=3, column=1, padx=5, pady=5)

        # Фото (рамка фиксированного размера)
        tk.Label(self, text="Фото:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.photo_frame = tk.Frame(self, width=200, height=200, bg="gray")
        self.photo_frame.grid(row=4, column=1, padx=5, pady=5)
        self.photo_frame.grid_propagate(False)

        self.photo_label = tk.Label(self.photo_frame, bg="gray")
        self.photo_label.pack(expand=True)

        tk.Button(self, text="Загрузить фото", command=self.load_photo).grid(row=5, column=1, pady=10)

        # Кнопки управления
        tk.Button(self, text="Сохранить", command=self.save_person).grid(row=6, column=0, pady=20)
        tk.Button(self, text="Отмена", command=self.clear_form).grid(row=6, column=1, pady=20)
        tk.Button(self, text="Выйти", command=self.destroy).grid(row=7, column=1, pady=10)

    def load_photo(self):
        """Загрузить фото и отобразить"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.photo_path = file_path
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=photo)
            self.photo_label.image = photo

    def clear_form(self):
        """Очистить форму"""
        self.first_name_var.set("")
        self.middle_name_var.set("")
        self.last_name_var.set("")
        self.mobile_var.set("")
        self.photo_label.config(image="")
        self.photo_label.image = None
        self.photo_path = None

    def save_person(self):
        """Сохранение записи через db_utils"""
        first_name = self.first_name_var.get().strip().capitalize()
        middle_name = self.middle_name_var.get().strip().capitalize()
        last_name = self.last_name_var.get().strip().capitalize()
        mobile = self.mobile_var.get().strip()

        if not (first_name and last_name and mobile):
            messagebox.showerror("Ошибка", "Имя, фамилия и мобильный обязательны!")
            return

        try:
            db_utils.save_person(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                mobile1=mobile,
                photo_path=self.photo_path
            )
            messagebox.showinfo("Успех", "Персона успешно сохранена!")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))


def run_form():
    app = PersonForm()
    app.mainloop()


if __name__ == "__main__":
    run_form()
