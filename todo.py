import tkinter as tk
from tkinter import ttk

class Todo:
    def __init__(self, frame, title, body):
        self.frame = tk.Frame(frame, bg="lightblue")
        lbl = ttk.Label(self.frame, text=title)
        text = tk.Text(self.frame, height=3)
        text.insert("1.0", body)
        btn = ttk.Button(self.frame, text="Finish")
        lbl.pack(fill="both", expand=True, padx=10, pady=10)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        btn.bind("<Button-1>", lambda event: self.frame.destroy())

def createOnFrame(frame, lable, input):
    Todo(frame, lable.get(), input.get())
    lable.delete(0, tk.END)
    input.delete(0, tk.END)
    
def update_scrollregion(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(canvas.find_all()[0], width=canvas.winfo_width())

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("TODO") 
    scrollbar = ttk.Scrollbar(root)
    scrollbar.pack(side="right", fill="y")
    canvas = tk.Canvas(root, yscrollcommand=scrollbar.set)
    frame_control = tk.Frame(root, bg="lightgray")
    frame_control.pack(side="right", fill="y", padx=10, pady=10)
    canvas.pack(side="left", fill="both", expand=True)
    tk.Label(frame_control, text="Title", bg="lightgray").pack(pady=10)
    lable = tk.Entry(frame_control, width=50)
    lable.pack(padx=10, pady=10)
    tk.Label(frame_control, text="Body", bg="lightgray").pack()
    input = tk.Entry(frame_control, width=50)
    input.pack(padx=10, pady=10)
    frame = tk.Frame(canvas)
    button = ttk.Button(frame_control, text="Create", width=30, command=lambda: createOnFrame(frame, lable, input))
    button.pack(padx=10, pady=10)
    
    
    canvas.create_window(0, 0, window=frame, anchor="nw", width=canvas.winfo_width())
    scrollbar.config(command=canvas.yview)

    frame.bind('<Configure>', lambda event: update_scrollregion(canvas))
    canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas.find_all()[0], width=canvas.winfo_width()))

    root.bind("<Delete>", lambda event: createOnFrame(frame, lable, input))
    root.bind("<Escape>", lambda event: root.destroy())
    root.mainloop()