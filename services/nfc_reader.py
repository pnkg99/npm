import threading
import time
from smartcard.System import readers
from smartcard.util import toHexString

def clean_ascii_data(raw_data):
    """Filter printable ASCII characters from raw byte data."""
    return ''.join(chr(byte) for byte in raw_data if 32 <= byte <= 126)

class NFCReader:
    """
    Ova klasa se bavi logikom povezivanja sa NFC čitačem,
    pokretanja niti za beskonačnu petlju, čitanja UID-a i token-a.
    Kad uspe da očita token, poziva callback u glavnoj Tkinter niti.
    """
    def __init__(self, root, on_card_read):
        """
        :param root: referenca na Tk ili neki Frame, da možemo koristiti root.after(...)
        :param on_card_read: funkcija (token, uid) -> None, koju zovemo kad očitamo karticu
        """
        self.root = root
        self.on_card_read = on_card_read

        self.reader = None
        self.connection = None

        self.monitor_thread = None
        self.keep_reading = False

    def start(self):
        """Pokreće NFC čitač i background nit."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            # Već radi
            return

        # Prvo, uverimo se da postoji bar jedan NFC čitač
        available_readers = readers()
        if not available_readers:
            print("Nema NFC čitača, ne mogu pokrenuti monitoring!")
            return

        self.reader = available_readers[0]
        print(f"[NFCReader] Korišćeni reader: {self.reader}")

        # Kreiraj inicijalnu konekciju
        self.connection = self.reader.createConnection()
        print("[NFCReader] Konekcija uspešno kreirana.")

        self.keep_reading = True
        self.monitor_thread = threading.Thread(target=self._read_card_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """Zaustavlja background nit i raskida konekciju."""
        self.keep_reading = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.monitor_thread = None

        self.connection = None
        self.reader = None
        print("[NFCReader] Zaustavljen reader.")

    def _read_card_loop(self):
        """Beskonačna petlja koja pokušava da se spoji na karticu i očita token."""
        BLOCK_SIZE = 4
        while self.keep_reading:
            try:
                self.connection.connect()
                
                # 1) Očitaj UID
                GET_UID_COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                response, sw1, sw2 = self.connection.transmit(GET_UID_COMMAND)
                uid = None
                if sw1 == 0x90 and sw2 == 0x00:
                    uid = ''.join(format(x, '02X') for x in response)

                # 2) Očitaj 32 bloka po 4 bajta
                token_accumulator = ""
                for block in range(32):
                    READ_COMMAND = [0xFF, 0xB0, 0x00, block, BLOCK_SIZE]
                    response, sw1, sw2 = self.connection.transmit(READ_COMMAND)
                    if sw1 == 0x90 and sw2 == 0x00:
                        ascii_chunk = clean_ascii_data(response)
                        if ascii_chunk:
                            token_accumulator += ascii_chunk

                self.connection.disconnect()

                # token_accumulator = token_accumulator[-100:] ili kako god treba
                token_accumulator = token_accumulator[-100:]
                print("[NFCReader] Pročitani token:", token_accumulator)
                print("[NFCReader] UID:", uid)

                # Pozivamo callback u glavnoj (tkinter) niti
                def callback():
                    self.on_card_read(token_accumulator, uid if uid else "")
                self.root.after(0, callback)

                time.sleep(0.5)
            except Exception as e:
                # Najčešće: nema kartice prisutne
                time.sleep(0.5)

        print("[NFCReader] Izlazak iz _read_card_loop.")
