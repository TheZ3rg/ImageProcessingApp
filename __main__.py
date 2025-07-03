import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np
import cv2

class ImageProcessingApp:
    def __init__(self):
        """Метод инициализации, в котором создается главное окно приложения,
        задаются его название и размер, вызываются методы для создания виджетов и
        запуска работы приложения."""
        self.root = tk.Tk()
        self.root.title("Редактор изображений")
        self.root.geometry("1200x800")
        
        self.image = None
        self.display_image = None

        self.create_widgets()

        self.root.mainloop()

    def create_widgets(self):
        """Создание виджетов приложения."""
        #Фрейм для кнопок из первой верхней строки
        top_buttons_frame = tk.Frame(self.root)
        top_buttons_frame.pack(pady=10)

        button_font = ("Arial", 16)

        tk.Button(top_buttons_frame,
                  text="Загрузить изображение",
                  command=self.load_image,
                  font=button_font).grid(row=0, column=0)
        tk.Button(top_buttons_frame,
                  text="Сделать снимок",
                  command=self.capture_from_webcam,
                  font=button_font).grid(row=0, column=1)
        
        #Создание кнопки-меню выбора канала отображения
        #Относиться к первому верхнему фрейму
        self.channel_var = tk.StringVar(value="Оригинал")
        options = ["Оригинал","Красный канал","Синий канал","Зеленый канал"]
        
        channel_menu = tk.OptionMenu(top_buttons_frame, self.channel_var, *options,
                      command=self.change_channel)
        channel_menu.config(font=('Arial', 16))
        channel_menu.grid(row=0, column=2, padx=10)

        #Фрейм для кнопок из второй верхней строки
        top_buttons_frame_2 = tk.Frame(self.root)
        top_buttons_frame_2.pack()

        tk.Button(top_buttons_frame_2,
                  text="Изменить яркость",
                  command=self.increase_brightness,
                  font=button_font).grid(row=0, column=0, padx=5)
        tk.Button(top_buttons_frame_2,
                  text="Изменить резкость",
                  command=self.sharpen_image,
                  font=button_font).grid(row=0, column=1, padx=5)
        tk.Button(top_buttons_frame_2,
                  text="Нарисовать прямоугольник",
                  command=self.draw_rectangle,
                  font=button_font).grid(row=0, column=2, padx=5)
        
        #Канвас для изображения
        self.img_canvas = tk.Canvas(self.root, width=1000, height=600, bg='gray')
        self.img_canvas.pack(pady=10)

        #Фрейм для кнопок из нижней строки
        bottom_buttons_frame = tk.Frame(self.root)
        bottom_buttons_frame.pack()

        tk.Button(bottom_buttons_frame,
                  text="Сохранить как",
                  command=self.save_image,
                  font=button_font).grid(row=0, column=0, padx=5)
        tk.Button(bottom_buttons_frame,
                  text="Сбросить изменения",
                  command=self.reset_changes,
                  font=button_font).grid(row=0, column=1, padx=5)

    def load_image(self):
        """Загрузка изображения через диалоговое окно."""
        filetypes = [("Image files", "*.jpg *.png")]
        filepath = filedialog.askopenfilename(
            title="Загрузить изображение",
            filetypes=filetypes
            )

        if filepath:
            try:
                with open(filepath, 'rb') as f:
                    img_data = np.frombuffer(f.read(), dtype=np.uint8)
                self.image = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

                if self.image is None:
                    raise Exception("Недопустимый файл изображения")
                
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.display_image = self.image.copy()
                self.update_image()
            except Exception as e:
                messagebox.showerror("Ошибка",
                                     f"Невозможно загрузить изображение: {str(e)}")

    def capture_from_webcam(self):
        """Получение изображение с вебкамеры."""
        try:
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                raise Exception("Не удалось подключиться к камере." \
                " Проверьте доступ и попробуйте еще раз")
        
            ret, frame = cap.read()
        
            cap.release()
            
            if not ret:
                raise Exception("Не удалось получить кадр")
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            self.image = frame
            self.display_image = self.image.copy()
            self.update_image()
             
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")


    def update_image(self):
        """Обновление изображения на канвасе."""

        h, w = self.display_image.shape[:2]
        ratio = min(1000/w, 600/h)
        new_size = (int(w*ratio), int(h*ratio))
        resized_image = cv2.resize(self.display_image, new_size)

        self.tk_image = ImageTk.PhotoImage(Image.fromarray(resized_image))
            
        self.img_canvas.delete("all")
        self.img_canvas.config(width=new_size[0], height=new_size[1])
        self.img_canvas.create_image(new_size[0]//2,
                                     new_size[1]//2,
                                     image=self.tk_image)
    
    def change_channel(self, *args):
        """Изменяет цветовой канал отображаемого изображения"""
        channel = self.channel_var.get()
        if channel == "Оригинал":
            self.display_image = self.image.copy()
        else:
            zeros = np.zeros_like(self.image[:, :, 0])
            channel_dict = {
            "Красный канал": [self.image[:, :, 0], zeros, zeros],  # R
            "Зеленый канал": [zeros, self.image[:, :, 1], zeros],  # G
            "Синий канал": [zeros, zeros, self.image[:, :, 2]]     # B
        }
            self.display_image = cv2.merge(channel_dict[channel])

        self.update_image()

    def increase_brightness(self):
        """Увеличивает яркость на процент, введенный пользователем"""
        if self.display_image is None:
                messagebox.showwarning("Ошибка", "Сначала загрузите изображение")
                return
        try:
            # Запрос процента яркости у пользователя
            percent = simpledialog.askfloat(
                "Регулировка яркости",
                "Введите процент изменения яркости (от -100 до 100):",
                minvalue=-100,
                maxvalue=100
            )
        
            if percent is None:
                return
                
            hue, saturation, value =  cv2.split(cv2.cvtColor(self.display_image,
                                                              cv2.COLOR_RGB2HSV))
            
            if percent >= 0: # Увеличение яркости
                value = np.where(value * (1 + percent/100) > 255,
                                  255,
                                  value * (1 + percent/100))
            else: # Уменьшение яркости
                value = value * (1 + percent/100)
            
            value = value.astype(np.uint8)
            
            bright_img = cv2.merge((hue, saturation, value))
            self.display_image = cv2.cvtColor(bright_img, cv2.COLOR_HSV2RGB)
            self.update_image()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")  

    def sharpen_image(self):
        """Увеличивает резкость с настраиваемой силой"""
        if self.display_image is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите изображение")
            return

        try:
            # Запрос силы резкости у пользователя
            strength = simpledialog.askfloat(
                "Настройка резкости",
                "Введите силу резкости (0.1-5.0, где 1.0 - стандартное значение):",
                initialvalue=1.0,
                minvalue=0.1,
                maxvalue=5.0
            )
            
            if strength is None:
                return

            blurred = cv2.GaussianBlur(self.display_image, (0, 0), 5)
            unsharp_image = cv2.addWeighted(
                self.display_image, 1.0 + strength,
                blurred, -strength,
                0
            )
            
            self.display_image = np.clip(unsharp_image, 0, 255).astype(np.uint8)
            self.update_image()

        except Exception as e:
            messagebox.showerror("Ошибка",
                                  f"Не удалось повысить резкость: {str(e)}")
            
    def draw_rectangle(self):
        """Рисует синий прямоугольник по координатам от пользователя"""
        if self.display_image is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите изображение")
            return

        try:
            # Запрос координат у пользователя
            coords = simpledialog.askstring(
                "Координаты прямоугольника",
                "Введите координаты левой верхней и правой нижней вершин в формате 'x1 y1 x2 y2':\n"
                "Например: 100 100 200 300"
            )
            if not coords: return 

            try:
                x1, y1, x2, y2 = map(int, coords.split())
            except ValueError:
                messagebox.showerror("Ошибка", "Неправильный формат координат")
                return

            h, w = self.display_image.shape[:2]
            if not (0 <= x1 < x2 < w and 0 <= y1 < y2 < h):
                messagebox.showerror("Ошибка",
                                     f"Координаты вне границ изображения. Размер изображения: {h, w}")
                return

            cv2.rectangle(
                self.display_image,
                (x1, y1),
                (x2, y2),
                color=(0, 0, 255),  # RGB
                thickness=2         # Толщина 2px
            )

            self.update_image()

        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Не удалось нарисовать прямоугольник: {str(e)}")

    def save_image(self):
        """Сохранение изображения в выбранную папку"""
        if self.display_image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение!")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("Все файлы", "*.*")]
        )

        if save_path:
            Image.fromarray(self.display_image).save(save_path)
            messagebox.showinfo("Успех", f"Изображение сохранено в:\n{save_path}")

    def reset_changes(self):
        """Возвращает изображение к исходному виду."""
        self.display_image = self.image.copy()
        self.update_image()

if __name__ == "__main__": 
    ImageProcessingApp()