import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

TEMP_FILE = "time_status.txt"


def write_temp(seconds):
    with open(TEMP_FILE, "w") as f:
        f.write(str(int(seconds)))

def read_temp():
    if not os.path.exists(TEMP_FILE):
        return 0
    with open(TEMP_FILE, "r") as f:
        data = f.read().strip()
        return int(data) if data else 0

class FocusMiniTimer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Timer")
        self.geometry("260x360")
        self.minsize(240, 320)
        self.configure(fg_color="black")

        self.running = False
        self.paused = False
        self.after_id = None

        self.total_seconds = 0
        self.remaining = 0
        self.elapsed = 0

        self.play_img = ctk.CTkImage(Image.open("images/play.png"), size=(26, 26))
        self.pause_img = ctk.CTkImage(Image.open("images/pause.png"), size=(26, 26))
        self.reset_img = ctk.CTkImage(Image.open("images/reset.png"), size=(26, 26))

        self.grid_rowconfigure(0, weight=4)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.canvas.bind("<Configure>", self.redraw_circle)

        self.status_label = ctk.CTkLabel(self, text="", font=("Segoe UI Semibold", 18, "bold"), text_color="white")
        self.status_label.grid(row=1, column=0)

        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.grid(row=2, column=0, sticky="ew", padx=12)
        self.controls.columnconfigure(0, weight=1)

        self._slider_row("Min", 0)
        self._slider_row("Sec", 1)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, pady=10)

        self.play_pause_btn = ctk.CTkButton(btn_frame, image=self.play_img, text="", width=42, height=42, fg_color="#111111", hover_color="#1f1f1f", command=self.play_pause)
        self.stop_btn = ctk.CTkButton(btn_frame, image=self.reset_img, text="", width=42, height=42, fg_color="#111111", hover_color="#1f1f1f", command=self.stop)
        # self.add_btn = ctk.CTkButton(btn_frame, text="Add Data", width=70, height=30,fg_color="#222", hover_color="#1f1f1f", command=self.add_data)

        self.play_pause_btn.pack(side="left", padx=6)
        self.stop_btn.pack(side="left", padx=6)

    def _slider_row(self, label, row):
        frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=4)
        frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text=label, width=35).grid(row=0, column=0)

        slider = ctk.CTkSlider(frame, from_=0, to=59, number_of_steps=59)
        slider.grid(row=0, column=1, sticky="ew", padx=6)
        slider.set(0)

        value = ctk.CTkLabel(frame, text="0", width=28)
        value.grid(row=0, column=2)

        slider.configure(command=lambda v, l=value: l.configure(text=str(int(v))))

        if label == "Min":
            self.min_slider, self.min_value = slider, value
        else:
            self.sec_slider, self.sec_value = slider, value

    def redraw_circle(self, _=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        size = min(w, h) - 60
        cx, cy = w // 2, h // 2
        stroke = max(6, size // 25)

        x1, y1 = cx - size // 2, cy - size // 2
        x2, y2 = cx + size // 2, cy + size // 2

        self.canvas.create_oval(x1, y1, x2, y2, outline="#222", width=stroke)
        self.arc_fg = self.canvas.create_arc(x1, y1, x2, y2,start=90,extent=-360, style="arc", outline="#4aa3ff",width=stroke)
        self.time_text = self.canvas.create_text(cx, cy,text="00:00",fill="white",font=("Segoe UI Semibold", max(16, size // 7)))

    def play_pause(self):
        if not self.running:
            self.start()
            return

        self.paused = not self.paused
        self.play_pause_btn.configure(image=self.play_img if self.paused else self.pause_img)

    def start(self):
        self.total_seconds = int(self.min_slider.get()) * 60 + int(self.sec_slider.get())
        if self.total_seconds <= 0:
            return

        self.remaining = self.total_seconds
        self.elapsed = 0
        write_temp(0)

        self.running = True
        self.paused = False
        self.play_pause_btn.configure(image=self.pause_img)
        self.tick()

    def stop(self):
        if self.after_id:
            self.after_cancel(self.after_id)

        self.running = False
        self.paused = False
        self.play_pause_btn.configure(image=self.play_img)
        self.canvas.itemconfigure(self.time_text, text="00:00")
        self.canvas.itemconfigure(self.arc_fg, extent=-360, outline="#4aa3ff")
        self.status_label.configure(text="")

    def tick(self):
        if not self.running:
            return

        if not self.paused:
            self.remaining -= 0.1
            self.elapsed += 0.1
            write_temp(self.elapsed)

            if self.remaining <= 0:
                self.finish()
                return

            total = int(self.remaining)
            m, s = divmod(total, 60)

            progress = self.remaining / self.total_seconds
            color = "red" if total <= 10 else "#4aa3ff"

            self.canvas.itemconfigure(self.time_text, text=f"{m:02d}:{s:02d}")
            self.canvas.itemconfigure(self.arc_fg,extent=-360 * progress,outline=color)

        self.after_id = self.after(100, self.tick)

    def finish(self):
        self.running = False
        self.paused = False
        self.play_pause_btn.configure(image=self.play_img)
        self.canvas.itemconfigure(self.time_text, text="00:00")
        self.canvas.itemconfigure(self.arc_fg, outline="red", extent=0)
        self.status_label.configure(text="TIME UP ")


if __name__ == "__main__":
    FocusMiniTimer().mainloop()