from Pages.base import BaseFrame, ttk
from services.web_api import read_nfc_card, logout
from services.nfc_reader import NFCReader 

class UserPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        lbl = ttk.Label(self.box_frame, text="Pročitajte karticu", font=("Helvetica", 16))
        lbl.pack(pady=10, anchor="center")

        lbl2 = ttk.Label(
            self.box_frame,
            text=(
                "Molimo vas da umetnete/priđete karticom čitaču. "
                "Aplikacija će automatski pokušati da očita token sa kartice. "
                "Kada se token uspešno detektuje, prelazimo na sledeću stranicu."
            ),
            font=("Helvetica", 10),
            wraplength=400,
            justify="left"
        )
        lbl2.pack(pady=10, anchor="center")

        btn_logout = ttk.Button(
            self.box_frame,
            text="Izloguj me",
            command=self.log_out
        )
        btn_logout.pack(pady=20)

        # Napravimo NFCReader, prosledimo: root -> self i callback -> self.on_card_read
        self.nfc_reader = NFCReader(self, self.on_card_read)

    def on_show(self):
        """Poziva se kad prelazimo na ovu stranicu. Pokrećemo background nit."""
        print("[UserPage] start nfc_reader")
        self.nfc_reader.start()

    def on_hide(self):
        """Poziva se kad napuštamo ovu stranicu. Gasi background nit."""
        print("[UserPage] stop nfc_reader")
        self.nfc_reader.stop()

    def on_card_read(self, token, uid):
        """Callback zvan iz NFCReader kada je očitan token + uid."""
        print(f"[UserPage] on_card_read => uid: {uid}, token: {token[:10]}...")
        response = read_nfc_card(self.controller.bearer_token , token, uid)
        if response :
            self.controller.balance = response["balance"]
            self.controller.slug = response["slug"]
            if self.controller.user_group_id == 5 :  
                self.controller.show_frame("ProductsPage")
            else :
                self.controller.show_frame("AdminPage")
        else:
            print("[UserPage] Neuspešna verifikacija kartice (read_nfc_card).")
    
    def log_out(self) :
        resp = logout(self.controller.bearer_token)
        if resp :
            self.controller.show_frame("LoginPage")
