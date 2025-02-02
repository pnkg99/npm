import threading
import time

import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C, MIFARE_CMD_AUTH_B

# Pomoćna funkcija za pretvaranje bajtova u čitljiv ASCII
def clean_ascii_data(raw_data):
    """Filteruje samo štampajuće ASCII znakove iz raw byte niza."""
    return ''.join(chr(byte) for byte in raw_data if 32 <= byte <= 126)

class NFCReader:
    """
    Klasa za asinkrono čitanje NFC tagova koristeći Adafruit PN532 modul preko I2C.
    Kada se pronađe kartica, očitavaju se UID i (opcionalno) MIFARE blokovi,
    pa se poziva callback (u glavnom Tkinter thread-u).
    """

    def __init__(self, root, on_card_read):
        """
        :param root: referenca na Tk/Frame radi poziva root.after(...)
        :param on_card_read: funkcija (token, uid) -> None, poziva se kada očitamo karticu
        """
        self.root = root
        self.on_card_read = on_card_read

        # Inicijalizacija I2C i PN532
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(i2c, debug=False)
        self.pn532.SAM_configuration()

        # Dodatne promenljive
        self.monitor_thread = None
        self.keep_reading = False

        print("PN532 uspešno inicijalizovan.")
        ic, ver, rev, support = self.pn532.firmware_version
        print(f"PN532 Firmware Version: {ver}.{rev}")

    def start(self):
        """Pokreće background nit za čitanje NFC tagova."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            # Već radi
            return
        self.keep_reading = True
        self.monitor_thread = threading.Thread(target=self._read_card_loop, daemon=True)
        self.monitor_thread.start()
        print("[NFCReader] Monitoring startovan.")

    def stop(self):
        """Zaustavlja background nit."""
        self.keep_reading = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.monitor_thread = None
        print("[NFCReader] Monitoring zaustavljen.")

    def _read_card_loop(self):
        """
        Beskonačna petlja koja proverava da li je NFC tag prisutan.
        Ako se očita UID, po želji čitamo 32 bloka MIFARE memorije,
        formiramo 'token_accumulator' i pozivamo callback.
        """
        while self.keep_reading:
            # read_passive_target pokušava da očita UID od kartice/tag-a
            uid = self.pn532.read_passive_target(timeout=0.5)
            if uid:
                print(f"[NFCReader] Kartica detektovana! UID = {[hex(i) for i in uid]}")
                
                # Opcionalno: pokušaj čitanja MIFARE klasičnih blokova
                token_accumulator = self._read_mifare_blocks(uid)

                # Pozivamo callback (u glavnom Tk thread-u)
                def callback():
                    # Stavljamo uid u hex string (npr. "AB12EF")
                    uid_hex = ''.join(f"{x:02X}" for x in uid)
                    self.on_card_read(token_accumulator, uid_hex)
                self.root.after(0, callback)

            time.sleep(0.2)

        print("[NFCReader] Napuštam _read_card_loop.")

    def _read_mifare_blocks(self, uid):
        """
        Pokušaj da očita 32 bloka MIFARE 1K (svaki 16 bajtova),
        uz pretpostavku da koristimo KEY B [0xFF]*6.
        Ako treba KEY A ili druga šema autentikacije, ovde izmeni.
        Vrati spojeni 'ASCII' sadržaj blokova.
        """
        token_accumulator = ""
        # Pazi: svaka stara MIFARE 1K ima 16 sektora x 4 bloka = 64 bloka (0..63),
        # ali adafruit primeri često čitaju prvih 32 bloka. Prilagodi po potrebi.
        for block_num in range(32):
            try:
                # Prvo se autentikujemo KEY B (može i MIFARE_CMD_AUTH_A)
                if not self.pn532.mifare_classic_authenticate_block(
                    uid, block_num, MIFARE_CMD_AUTH_B, [0xFF]*6
                ):
                    # Autentikacija neuspešna - preskačemo blok
                    continue
                
                # Ako je uspešno, čitamo blok
                block_data = self.pn532.mifare_classic_read_block(block_num)
                if block_data:
                    ascii_chunk = clean_ascii_data(block_data)
                    token_accumulator += ascii_chunk
            except Exception as e:
                # Možda greška pri čitanju
                # print(f"Greška u čitanju bloka {block_num}: {e}")
                pass

        # primer da uzmemo poslednjih 100 karaktera
        token_accumulator = token_accumulator[-100:]
        print(f"[NFCReader] Pročitano iz blokova: {token_accumulator}")
        return token_accumulator
