import tkinter as tk
from tkinter import ttk

class OnScreenKeyboard(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Virtual Keyboard")

        # Glavni frejm
        frame = ttk.Frame(self)
        frame.pack()

        # Primer samo jednog reda slova
        letters = "QWERTYUIOP"
        for letter in letters:
            btn = ttk.Button(frame, text=letter, command=lambda l=letter: self._on_click(l))
            btn.pack(side="left", padx=2, pady=2)

        # Backspace i Enter primer
        btn_bs = ttk.Button(frame, text="Back", command=self._backspace)
        btn_bs.pack(side="left", padx=2, pady=2)

        btn_enter = ttk.Button(frame, text="Enter", command=self._enter)
        btn_enter.pack(side="left", padx=2, pady=2)

    def _on_click(self, letter):
        # Ubacuje karakter u "fokusirani" widget
        widget = self.focus_get()
        if isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
            widget.insert(tk.INSERT, letter)

    def _backspace(self):
        widget = self.focus_get()
        if isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
            current = widget.get()
            widget.delete(0, tk.END)
            widget.insert(tk.END, current[:-1])

    def _enter(self):
        # Primer: moze nesto da radi, ili samo novi red
        widget = self.focus_get()
        if isinstance(widget, tk.Entry):
            # Možda 'potvrdi' unos?
            print("Submitted:", widget.get())
        elif isinstance(widget, tk.Text):
            widget.insert(tk.END, "\n")
            
if __name__ == "__main__":
    app = OnScreenKeyboard()
    app.mainloop()
