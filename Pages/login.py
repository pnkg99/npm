from Pages.base import tk, ttk, BaseFrame
from services.web_api import login, get_products

class LoginPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # 2) U samom box-u postavljamo login elemente
        
        style = ttk.Style(self)
        style.configure(
            "BigEntry.TEntry",
            padding=(10, 5),           # (left/right, top/bottom) - unutrašnji razmak
            font=("Helvetica", 18),     # veći font => veća visina
            height = 10
        )
        lbl_title = tk.Label(self.box_frame, text="Ulogujte se", font=("Helvetica", 22))
        lbl_title.pack(pady=20)
        
        self.email_var = tk.StringVar(value="nektarpivo@arsenalfest2025.rs")
        self.email_var = tk.StringVar(value="prodajakartica@arsenalfest2025.rs")
        self.email_entry = ttk.Entry(self.box_frame, style="BigEntry.TEntry", textvariable=self.email_var, width=300)
        self.email_entry.pack(padx=20, pady=5)  # spoljašnji razmak od ivica ekrana

        self.password_var = tk.StringVar(value="12345678")
        self.password_entry = ttk.Entry(self.box_frame, style="BigEntry.TEntry", textvariable=self.password_var, show="*", width=300)
        self.password_entry.pack(padx=20, pady=5)
        
        # 3) Dugme za login
        login_button = tk.Button(
            self.box_frame,
            text="Ulogujte se",
            command=self.login_action,
            bg="blue",       # pozadina
            fg="white",      # tekst
            activebackground="#002080",  # nijansa kad je pritisnuto (opciono)
            activeforeground="white",
            width=300,
            font=("Helvetica", 16)
        )
        login_button.pack(pady=10, padx=20)

    def login_action(self):
        email = self.email_var.get()
        password = self.password_var.get()

        response_data = login(email, password)
        
        if response_data :
            # Uspešan login
            self.controller.bearer_token = response_data["token"]
            self.controller.user_group_id = response_data["user_group_id"]
            # Na osnovu user_group_id pokazujemo odgovarajuću stranicu
            if self.controller.user_group_id == 5:
                products = get_products(self.controller.bearer_token)
                self.controller.products = products
            else:
                # Prikaži poruku o grešci, npr.:
                print("Neuspešan login ili greška na serveru.")
            self.controller.show_frame("UserPage")
        else:
            # Neuspešan login ili greška pri pozivu
            print("Neuspešan login ili došlo je do greške.")