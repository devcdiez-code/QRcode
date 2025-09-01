import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from init_pkg import db_init, db_utils

PHOTO_FRAME_WIDTH = 15
PHOTO_FRAME_HEIGHT = 20


FORM_FRAME_WIDTH = 500  #  ширина  в пикселях
FORM_FRAME_HEIGHT = 550 # высота  в пикселях

class PersonForm(tk.Tk):
    def __init__(self):
        super().__init__()
        # geometry_str = f"{}x{}+{offset_x}+{offset_y}"
        geometry_str = f"{FORM_FRAME_WIDTH}x{FORM_FRAME_HEIGHT}"
        print (" size frame:" , geometry_str)
        self.title(f"Добавить персону          {geometry_str}")
        self.geometry(geometry_str)

        #self.resizable(False, False)
        self.resizable(True, True)


        # --- блок фото ---
        self.photo_label = tk.Label(self, text="Фото не загружено", width=PHOTO_FRAME_WIDTH, height=PHOTO_FRAME_HEIGHT, relief="sunken")
        self.photo_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.photo_label.grid_propagate(False)

        #self.photo_label = Label(root, width=label_width, height=label_height, bg="gray")
        #self.photo_label.pack()

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

    def clear_form(self):
        """Очистить форму"""
        self.entry_last.delete(0, tk.END)
        self.entry_first.delete(0, tk.END)
        self.entry_middle.delete(0, tk.END)
        self.entry_mobile.delete(0, tk.END)
        self.photo_label.config(image="", text="Фото не загружено")
        self.photo_path = None

    def load_photo(self):
        """Загрузить фото с диска и отобразить"""
        path = filedialog.askopenfilename(
            filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        self.photo_path = path
        if not path:
            return

        # Загружаем картинку
        img = Image.open(path)

        # Масштабируем под размер  с сохранением пропорций
        img.thumbnail((PHOTO_FRAME_WIDTH, PHOTO_FRAME_HEIGHT), Image.Resampling.LANCZOS)  # фиксированный размер

        #img = img.resize((100, 100), Image.Resampling.LANCZOS)

        # Преобразуем в объект для Tkinter
        self.photo_imgtk = ImageTk.PhotoImage(img)

        # Устанавливаем фото в label ; Вставляем картинку
        #self.photo_label.config(image=self.photo_imgtk, text="")
        self.photo_label.config(image=self.photo_imgtk,text="")
        # self.photo_label = tk.Label (image = self.photo_imgtk)
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
            self.clear_form()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))





def run_form():
    app = PersonForm()
    app.mainloop()




if __name__ == "__main__":
    run_form()
