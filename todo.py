import tkinter as tk
from tkinter import ttk, messagebox
import os
from google.cloud import texttospeech
import pygame
import uuid
from datetime import datetime
import time
import threading

dir_name = os.path.dirname(__file__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(dir_name, "keys.json")
tasks_dir = os.path.join(dir_name, "tasks")
speeches_dir = os.path.join(dir_name, "speeches")


def speak(text_to_speak):
    if not text_to_speak:
        messagebox.showwarning("Ошибка", "Поле текста пустое!")
        return

    # Инициализация клиента Text-to-Speech
    client = texttospeech.TextToSpeechClient()

    # Настройка текста для синтеза
    synthesis_input = texttospeech.SynthesisInput(text=text_to_speak)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ru-RU",  # Русский язык
        name="ru-RU-Wavenet-A",  # Голос (WaveNet для естественного звучания)
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,  # Скорость речи
        pitch=0.0,  # Тон
    )

    # Запрос на синтез речи
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content


class Player:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, frame):
        if hasattr(self, "_initialized"):
            return

        self.queue = [
            todo.mp3_path for todo in frame.winfo_children() if isinstance(todo, Todo)
        ]
        self.index = 0
        self.running = False
        pygame.mixer.init()
        self._initialized = True
    
    def add(self, path):
        self.queue.append(path)

    def start(self):
        self.queue = [
            todo.mp3_path for todo in frame.winfo_children() if isinstance(todo, Todo)
        ]
        if not self.running:
            if self.index >= len(self.queue):
                self.index = 0
            self.running = True
            threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False
        pygame.mixer.music.stop()

    def _loop(self):
        while self.running and self.index < len(self.queue):
            path = self.queue[self.index]
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                # Ждём окончания текущего файла
                while self.running and pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                print(e)
            self.index += 1
        self.running = False


class Todo(ttk.Frame):
    def __init__(self, frame, title, body, old=None):
        tk.Frame.__init__(self, master=frame, bg="lightblue")

        self.update(old)
        self.setup_ui(title, body)

        if not old:  # если файл не создан
            self.save_file()
        else:
            self.pack(fill="both", expand=True, padx=4, pady=4)

    def setup_ui(self, title, body):
        self.idlbl = ttk.Label(
            self, text=f"{self.id} {self.updated}", font=("Arial", 6, "bold")
        )
        self.idlbl.pack(fill="both", expand=True, padx=4, pady=3)
        self.lbl = ttk.Label(self, text=title)
        self.text = tk.Text(self, height=3)
        self.text.insert("1.0", body)
        self.lbl.pack(fill="both", expand=True, padx=4, pady=4)
        self.text.pack(fill="both", expand=True, padx=4, pady=4)

        btn = ttk.Button(self, text="Finish")
        btn.pack(fill="both", expand=True, padx=4, pady=4)
        btn.bind("<Button-1>", lambda event: self.remove_self())

        play = ttk.Button(self, text="Play", command=self.play)

        save = ttk.Button(
            self, text="Save", command=lambda: self.save_file(rewrite=True)
        )
        save.pack(fill="both", expand=True, padx=4, pady=4)
        play.pack(fill="both", expand=True, padx=4, pady=4)

    def save_file(self, rewrite=False):
        if rewrite:
            os.remove(self.mp3_path)
            os.remove(self.text_path)
            self.update()
            self.idlbl.config(text=f"{self.id} {self.updated}")

        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write(self.lbl["text"] + "\n")
            f.write(self.text.get("1.0", tk.END))
        audio_content = speak(self.text.get("1.0", tk.END))

        with open(self.mp3_path, "wb") as out:
            out.write(audio_content)

    def remove_self(self):
        os.remove(self.mp3_path)
        os.remove(self.text_path)
        self.destroy()
        frame = self.master
        frame.update_idletasks()
        update_scrollregion(frame.master)

    def update(self, old=None):
        if old:
            self.updated = old.split("$")[0]
            self.id = old.split("$")[1]
        else:
            self.updated = datetime.now().strftime("%m-%d-%Y %H-%M-%S")
            self.id = uuid.uuid1().hex

        file_name = self.updated + "$" + self.id
        self.mp3_path = os.path.join(speeches_dir, file_name) + ".mp3"
        self.text_path = os.path.join(tasks_dir, file_name) + ".txt"

    def play(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.mp3_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Ждём окончания воспроизведения
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()

    def _play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.mp3_path)
        pygame.mixer.music.play()

    def playT(self):
        threading.Thread(target=self._play_music, daemon=True).start()

    def stop(self):
        pygame.mixer.music.stop()
        # self.sound.stop()


def createOnFrame(frame, lable, input):
    if input.get("1.0", tk.END).strip() == "":
        messagebox.showwarning("Ошибка", "Поле текста пустое!")
        return
    todo = Todo(frame, lable.get(), input.get("1.0", tk.END))
    todo.pack(
        fill="both", expand=True, padx=4, pady=4
    )
    
    lable.delete(0, tk.END)
    input.delete("1.0", tk.END)
    frame.update_idletasks()
    update_scrollregion(frame.master)


def update_scrollregion(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1.0)


def load(frame):
    for file in os.listdir(tasks_dir):
        with open(os.path.join(tasks_dir, file), "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip()

            Todo(frame, title, "\n".join(lines[1:]), old=file[:-4])


def set_control_frame(root, frame, player):
    frame_control = tk.Frame(root, bg="lightgray")
    frame_control.pack(side="right", fill="y", padx=10, pady=10)
    tk.Label(frame_control, text="Title", bg="lightgray").pack(pady=10)
    lable = tk.Entry(frame_control, width=50)
    lable.pack(padx=10, pady=10)
    tk.Label(frame_control, text="Body", bg="lightgray").pack()
    input = tk.Text(frame_control, width=50, height=7)
    input.pack(padx=10, pady=10)
    button = ttk.Button(
        frame_control,
        text="Create",
        width=30,
        command=lambda: createOnFrame(frame, lable, input),
    )
    button.pack(padx=10, pady=10)
    button = ttk.Button(
        frame_control, text="Play all", width=30, command=lambda: player.start()
    )
    button.pack(padx=10, pady=10)

    stop_button = ttk.Button(
        frame_control, text="Stop all", width=30, command=lambda: player.stop()
    )
    stop_button.pack(padx=10, pady=10)

    root.bind("<Delete>", lambda event: createOnFrame(frame, lable, input))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("TODO")
    scrollbar = ttk.Scrollbar(root)
    scrollbar.pack(side="right", fill="y")
    canvas = tk.Canvas(root, yscrollcommand=scrollbar.set)
    frame = tk.Frame(canvas)
    
    load(frame)
    player = Player(frame)
    set_control_frame(root, frame, player)

    canvas.pack(side="left", fill="both", expand=True)

    canvas.create_window(0, 0, window=frame, anchor="nw", width=canvas.winfo_width())
    scrollbar.config(command=canvas.yview)

    canvas.bind(
        "<Configure>",
        lambda e: canvas.itemconfig(canvas.find_all()[0], width=canvas.winfo_width()),
    )

    root.after(290, lambda: canvas.configure(scrollregion=canvas.bbox("all")))
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    root.bind("<Escape>", lambda event: root.destroy())

    root.mainloop()
