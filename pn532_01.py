import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C, MIFARE_CMD_AUTH_B

def clean_ascii_data(raw_data):
    """Filteruje samo štampajuće ASCII znakove iz raw byte niza."""
    return ''.join(chr(byte) for byte in raw_data if 32 <= byte <= 126)

class NFCReader:
    """
    Non-blocking NFC čitač uz Adafruit PN532 (I2C),
    čita i UID i prvih 32 bloka MIFARE Classic kartice.
    """

    def __init__(self, root, on_card_read):
        """
        :param root: Referenca na tk ili frame, da bismo mogli da koristimo root.after(...)
        :param on_card_read: callback(token, uid) -> ...
        """
        self.root = root
        self.on_card_read = on_card_read

        # Inicijalizacija PN532
        i2c = busio.I2C(board.SCL, board.SDA)
        self.pn532 = PN532_I2C(i2c, debug=False)
        self.pn532.SAM_configuration()
        
        ic, ver, rev, support = self.pn532.firmware_version
        print(f"[NFCReader] PN532 Firmware Version: {ver}.{rev}")

        self.check_interval_ms = 200  # koliki razmak između "provera" u milisekundama
        self.is_running = False

    def start(self):
        """Pokreće ciklično proveravanje (poll) u glavnom Tkinter thread-u."""
        if not self.is_running:
            self.is_running = True
            self._schedule_next_check()
            print("[NFCReader] Startovao non-blocking polling.")

    def stop(self):
        """Zaustavlja dalje ciklično proveravanje."""
        self.is_running = False
        print("[NFCReader] Zaustavljen.")

    def _schedule_next_check(self):
        """Planira sledeću proveru posle self.check_interval_ms ms."""
        if self.is_running:
            self.root.after(self.check_interval_ms, self._read_card_once)

    def _read_card_once(self):
        """Jedna provera: ako postoji kartica (MIFARE), očitava UID i 32 bloka."""
        if not self.is_running:
            return

        uid = self.pn532.read_passive_target(timeout=0.1)
        if uid:
            uid_hex = ''.join(f"{b:02X}" for b in uid)
            print(f"[NFCReader] Kartica detektovana! UID={uid_hex}")

            # Pokušaj da očitaš 32 bloka ako je MIFARE Classic:
            # (Ako nije MIFARE Classic, autentiikacija će propasti i dobićeš delimične ili nikakve podatke.)
            token_accumulator = ""
            # MIFARE Classic obično ima 64 bloka, ali možemo probati samo 32
            for block_num in range(32):
                try:
                    # Pokušamo KEY B (0xFF..)
                    if not self.pn532.mifare_classic_authenticate_block(
                        uid, block_num, MIFARE_CMD_AUTH_B, [0xFF]*6
                    ):
                        # Neuspešna autentikacija, preskačemo
                        continue
                    block_data = self.pn532.mifare_classic_read_block(block_num)
                    if block_data:
                        token_accumulator += clean_ascii_data(block_data)
                except Exception as e:
                    # Greška pri čitanju bloka (možda nije MIFARE, ili krivi ključ, itd.)
                    pass

            # Ako želiš samo poslednjih 100 karaktera
            token_accumulator = token_accumulator[-100:]
            print(f"[NFCReader] Iz blokova dobili token: {token_accumulator}")

            # Poziv callbacka
            def callback():
                self.on_card_read(token_accumulator, uid_hex)
            self.root.after(0, callback)

        # Zakazujemo sledeću proveru
        self._schedule_next_check()
