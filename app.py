import tkinter as tk
from tkinter import ttk
from Pages.login import LoginPage
from Pages.product import ProductsPage
from Pages.user import UserPage
from Pages.admin import AdminPage
  
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Demo aplikacija")
        # Postavlja full screen
        self.attributes("-fullscreen", True)

        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Kontejner (Frame) koji ce cuvati sve "stranice"
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        
        # Promenljive kroz aplikaciju
        self.user_group_id = 0
        self.products = []
        self.bearer_token=""
        self.slug=""
        self.balance=0
        
        # Svi frejmovi u aplikaciji
        self.frames = {}
        
        # Inicijalizujemo sve stranice
        for PageClass in (LoginPage, UserPage, ProductsPage, AdminPage):
            page_name = PageClass.__name__
            if PageClass == ProductsPage :
                frame = PageClass(parent=self, controller=self, products_list=self.products)
            else :
                frame = PageClass(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Prikazujemo login kao početnu
        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        """Metoda koja prikazuje određeni frejm po imenu."""
        frame = self.frames[page_name]
        
        if page_name == "ProductsPage":
            frame.show_products(self.products)
            
        for f_name, f_instance in self.frames.items():
            if hasattr(f_instance, "on_hide") and f_instance != frame:
                f_instance.on_hide()
        
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()
        

if __name__ == "__main__":
    app = App()
    app.mainloop()
