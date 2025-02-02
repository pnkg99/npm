from Pages.base import tk, ttk, BaseFrame
from services.web_api import change_balance

class AdminPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        # 1) Naslov (Račun), centriran
        lbl_title = ttk.Label(self.box_frame, text="Račun", font=("Helvetica", 16))
        lbl_title.pack(pady=10, anchor="center")

        # 1a) Labela koja prikazuje trenutno stanje (balance)
        self.lbl_balance = ttk.Label(self.box_frame, text="Stanje: 0 RSD", font=("Helvetica", 12))
        self.lbl_balance.pack(pady=5, anchor="center")

        # 2) Okvir (row_frame) u kojem će Combobox i Entry stajati jedno pored drugog
        row_frame = ttk.Frame(self.box_frame)
        row_frame.pack(pady=10)
        
        # Combobox (izbor akcije)
        self.var_action = tk.StringVar(value="Skidanje")  # podrazumevana opcija
        self.cb_action = ttk.Combobox(
            row_frame,
            textvariable=self.var_action,
            values=["Skidanje", "Dodavanje"],
            state="readonly"  # da ne kuca sam, već bira
        )
        self.cb_action.pack(side="left", padx=10)

        # Entry (iznos)
        self.var_amount = tk.StringVar()
        self.entry_amount = ttk.Entry(row_frame, textvariable=self.var_amount)
        self.entry_amount.pack(side="left", padx=10)

        # 3) Dugme "Sačuvaj izmene"
        btn_save = ttk.Button(
            self.box_frame,
            text="Sačuvaj izmene",
            command=self.on_save_click
        )
        btn_save.pack(pady=20)
        btn_cancel = ttk.Button(
            self.box_frame,
            text="Odustani",
            command=self.on_cancel
        )
        btn_cancel.pack(pady=20)


    def on_show(self):
        """Ova metoda se poziva kada prelaziš na AdminPage."""
        # (Možeš prvo pozvati roditeljski on_show, ako ga BaseFrame ima)
        # super().on_show()

        # Uzimamo novostavljeno self.controller.balance
        current_balance = getattr(self.controller, "balance", 0)
        self.lbl_balance.config(text=f"Stanje: {current_balance} RSD")

    def on_cancel(self):
        self.controller.show_frame("UserPage")

    def on_save_click(self):
        action = self.var_action.get()    # "Skidanje" ili "Dodavanje"
        amount_str = self.var_amount.get()
        print(f"[AdminPage] Sačuvaj izmene -> Action: {action}, Amount: {amount_str}")
        
        # Možeš ovde upotrebiti 'current_balance' i ažurirati ga
        try:
            amount = float(amount_str)
        except ValueError:
            print("Nije validan broj!")
            return

        # U zavisnosti od akcije, menjaš self.controller.balance
        if action == "Skidanje":
            self.controller.balance -= amount
            action_value = 1
        else:  # "Dodavanje"
            self.controller.balance += amount
            action_value = 2
        
        resp = change_balance(self.controller.bearer_token, self.controller.slug, action_value, amount)

        if resp :
        # Nakon promene balansa, eventualno odmah ažuriraj prikaz
            self.lbl_balance.config(text=f"Stanje: {self.controller.balance} RSD")
            print(f"Novo stanje je {self.controller.balance}")
            self.controller.show_frame("UserPage")