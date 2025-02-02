import tkinter as tk
from tkinter import ttk

# Opcionalno dodaj osnovni BaseFrame koji svi mogu naslediti
class BaseFrame(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        self.box_frame = tk.Frame(self.container, width=800, height=500,
            padx=100,
            pady=100,
            highlightthickness=2,
            highlightbackground="blue"
            )
        self.box_frame.pack_propagate(False)  # ne dozvoli da se Frame smanji na osnovu child widgeta
        self.box_frame.pack(expand=True)