import tkinter as tk
from services.web_api import checkout_service

class ProductsPage(tk.Frame):
    def __init__(self, parent, controller, products_list):
        super().__init__(parent)
        self.controller = controller
        self.products_list = products_list
        self.cart = []
        self.create_layout()

    def create_layout(self):
        # -- Konfigurisanje grid-a na nivou stranice --
        self.grid_rowconfigure(0, weight=1)                # gornji deo rastegljiv
        self.grid_rowconfigure(1, weight=0)                # donji deo (dugmad) fiksan
        self.grid_columnconfigure(0, weight=1)             # leva kolona rastegljiva
        self.grid_columnconfigure(1, weight=0)             # desna kolona - fiksna širina korpe

        # 1) Proizvodi (Levo)
        self.products_frame = tk.Frame(self, bg="#f0f0f0")  # Po želji malo drugačija boja
        self.products_frame.grid(row=0, column=0, sticky="nsew", padx=20)

        # 2) Korpa (Desno)
        self.cart_frame = tk.Frame(self, bg="#ddd", relief="groove", bd=2)
        self.cart_frame.grid(row=0, column=1, sticky="ns")

        self.cart_title = tk.Label(self.cart_frame, text="Korpa", font=("Helvetica", 18, "bold"), bg="#ddd")
        self.cart_title.pack(pady=10, padx=200)

        self.cart_items_frame = tk.Frame(self.cart_frame, bg="#ddd")
        self.cart_items_frame.pack(fill="both", expand=True)

        self.total_label = tk.Label(self.cart_frame, text="Ukupno: 0 RSD", font=("Helvetica", 20), bg="#ddd")
        self.total_label.pack(pady=(10, 0))

        # 3) Donji red sa dugmadima (Cancel 30%, Confirm 70%)
        self.buttons_frame = tk.Frame(self, bg="#ccc")
        self.buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=3)
        self.buttons_frame.grid_columnconfigure(1, weight=7)

        btn_cancel = tk.Button(
            self.buttons_frame, text="Otkazi",
            bg="red", fg="white", font=("Helvetica", 16, "bold"),cursor="hand2",height=3,
            command=self.cancel_purchase
        )
        btn_cancel.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        btn_confirm = tk.Button(
            self.buttons_frame, text="Potvrdi",
            bg="green", fg="white", font=("Helvetica", 16, "bold"),cursor="hand2",height=3,
            command=self.confirm_purchase
        )
        btn_confirm.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    def show_products(self, products_list):
        """Popunjava (ili osvežava) listu proizvoda (Leva kolona)."""
        for child in self.products_frame.winfo_children():
            child.destroy()

        lbl_title = tk.Label(
            self.products_frame, text="Dostupni proizvodi", 
            font=("Helvetica", 18, "bold"), bg="#f0f0f0"
        )
        lbl_title.grid(row=0, column=0, columnspan=3, pady=10, padx=(10, 0), sticky="w")

        cols = 3
        row_offset = 1
        for index, product in enumerate(products_list):
            r = (index // cols) + row_offset
            c = index % cols

            # 1) Kreiramo okvir za proizvod
            product_frame = tk.Frame(
                self.products_frame,
                bg="white",
                bd=1,
                relief="ridge",
                cursor="hand2"  # (Opcionalno) da pokazuje ruku pri hover-u
            )
            product_frame.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

            # 2) Bilo koji label ili opis proizvoda
            lbl_name = tk.Label(product_frame, text=product["name"], font=("Helvetica", 14, "bold"), bg="white")
            lbl_name.pack(pady=(20, 10), padx=5)

            lbl_price = tk.Label(product_frame, text=f"{product['price']} RSD", font=("Helvetica", 12, "bold"), bg="white")
            lbl_price.pack(pady=(10, 20))

            # 3) Umesto dugmeta, ceo frame reaguje na klik
            #    Kad se klikne (Button-1), pozivamo self.add_to_cart(product).
            #    Ovaj lambda hvata 'product' kao p.
            product_frame.bind("<Button-1>", lambda event, p=product: self.add_to_cart(p))

        # Rastegljivost kolona
        for col_index in range(cols):
            self.products_frame.grid_columnconfigure(col_index, weight=1)

        self.update_cart_display()

    ## ------------------- KORPA / CART LOGIKA -------------------

    def add_to_cart(self, product):
        """Dodaje ili uvećava proizvod."""
        for item in self.cart:
            if item["product"]["id"] == product["id"]:
                item["quantity"] += 1
                self.update_cart_display()
                return
        self.cart.append({"product": product, "quantity": 1})
        self.update_cart_display()

    def remove_one_from_cart(self, product_id):
        """Smanjuje količinu za 1 ili potpuno uklanja iz korpe ako padne na 0."""
        for item in self.cart:
            if item["product"]["id"] == product_id:
                item["quantity"] -= 1
                if item["quantity"] <= 0:
                    self.cart.remove(item)
                break
        self.update_cart_display()

    def remove_item_completely(self, product_id):
        """Potpuno uklanja stavku iz korpe, bez obzira na količinu."""
        for item in self.cart:
            if item["product"]["id"] == product_id:
                self.cart.remove(item)
                break
        self.update_cart_display()

    def add_one_to_cart(self, product_id):
        """Povećava količinu za 1."""
        for item in self.cart:
            if item["product"]["id"] == product_id:
                item["quantity"] += 1
                break
        self.update_cart_display()

    def update_cart_display(self):
        """Prikazuje stavke u korpi i računa total.
        Sada svaka stavka ima zaseban frejm (karticu),
        a u njemu gornji red s nazivom i cenom,
        i donji red s dugmadima."""

        # Očistimo prethodne prikaze
        for child in self.cart_items_frame.winfo_children():
            child.destroy()

        total_price = 0

        for item in self.cart:
            product = item["product"]
            quantity = item["quantity"]
            sum_price = product["price"] * quantity
            total_price += sum_price

            # 1) Kreiramo poseban frejm za SVAKU stavku (karticu)
            item_frame = tk.Frame(self.cart_items_frame, bg="#ccc", bd=2, relief="ridge")
            item_frame.pack(fill="x", padx=5, pady=5)

            # 2) Gornji red: Naziv, cena i total, sve u jednom labelu (ili više labela)
            #    Napravićemo jedan label s celim tekstom, ali možeš i odvojiti
            item_text = f"{product['name']} ( {product['price']} RSD ) x{quantity} = {sum_price} RSD"
            lbl_item = tk.Label(item_frame, text=item_text, bg="#ccc", font=("Helvetica", 14))
            lbl_item.pack(padx=5, pady=(5, 0), anchor="w")

            # 3) Donji red: Frejm za dugmad
            buttons_frame = tk.Frame(item_frame, bg="#ddd")
            buttons_frame.pack(fill="x", padx=5, pady=5)

            # 3c) Remove dugme
            btn_remove = tk.Button(
                buttons_frame, text="✖️", bg="red", fg="white",
                font=("Helvetica", 16, "bold"), height=2,
                command=lambda pid=product["id"]: self.remove_item_completely(pid)
            )
            btn_remove.pack(side="left", expand=True, fill="x", padx=2)

            # 3a) Minus dugme
            btn_minus = tk.Button(
                buttons_frame, text="➖", bg="orange", fg="white",
                font=("Helvetica", 16, "bold"), height=2,
                command=lambda pid=product["id"]: self.remove_one_from_cart(pid)
            )
            btn_minus.pack(side="left", expand=True, fill="x", padx=2)

            # 3b) Plus dugme
            btn_plus = tk.Button(
                buttons_frame, text="➕", bg="green", fg="white",
                font=("Helvetica", 16, "bold"), height=2,
                command=lambda pid=product["id"]: self.add_one_to_cart(pid)
            )
            btn_plus.pack(side="left", expand=True, fill="x", padx=2)



        # 4) Ažuriramo total
        self.total_label.config(text=f"Ukupno: {total_price} RSD")

    ## ------------------- CANCEL i CONFIRM -------------------

    def cancel_purchase(self):
        """Poništava korpu."""
        self.cart.clear()
        self.update_cart_display()
        # Vraćamo se na UserPage (ili koju već želiš)
        self.controller.show_frame("UserPage")

    def confirm_purchase(self):
        """Pokreće modal da pita: Jeste li sigurni?"""
        if not self.cart:
            print("Korpa je prazna.")
            return

        # 1) Kreiraj Toplevel (modal)
        confirm_window = tk.Toplevel(self)
        confirm_window.title("Potvrdi kupovinu")
        confirm_window.grab_set()  # Sprečava interakciju sa parent prozorom dok se modal ne zatvori

        # Centrira prozor (opciono)
        confirm_window.geometry("600x200+600+300")

        label_question = tk.Label(confirm_window, text="Da li ste sigurni?", font=("Helvetica", 20, "bold"))
        label_question.pack(pady=20)

        frame_btns = tk.Frame(confirm_window)
        frame_btns.pack(pady=10)
        
        btn_no = tk.Button(frame_btns, text="Ne", bg="red", fg="white", width=20,height=5, font=("Helvetica", 16, "bold"),
                           command=confirm_window.destroy)
        btn_no.pack(side="left", padx=5)

        btn_yes = tk.Button(frame_btns, text="Da", bg="green", fg="white", width=20, height=5, font=("Helvetica", 16, "bold"),
                            command=lambda: self.finalize_purchase(confirm_window))
        btn_yes.pack(side="left", padx=5)


    def finalize_purchase(self, confirm_window):
        """Ako korisnik klikne 'Da' - formira finalnu strukturu i šalje (ili ispisuje)."""
        confirm_window.destroy()  # Zatvaramo modal

        # Računamo total
        total_price = sum(item["product"]["price"] * item["quantity"] for item in self.cart)

        # Gradimo `cart` dict: key=product_id, value={name, price, quantity}
        cart_dict = {}
        for item in self.cart:
            pid = str(item["product"]["id"])
            cart_dict[pid] = {
                "name": item["product"]["name"],
                "price": item["product"]["price"],
                "quantity": item["quantity"]
            }

        # Konačna struktura
        payload = {
            "slug": self.controller.slug ,
            "totalAmount": total_price,
            "cart": cart_dict
        }

        resp = checkout_service(self.controller.bearer_token, self.controller.slug, total_price, cart_dict)

        if resp :
            print("Uspesno izvrsena kupovina")
            # Očistimo korpu i reset
            self.cart.clear()
            self.update_cart_display()

            self.controller.show_frame("UserPage")
