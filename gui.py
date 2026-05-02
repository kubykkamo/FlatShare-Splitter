import ttkbootstrap as tb
from ttkbootstrap.constants import *
from storage import DatabaseManager


class App:
    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager

        # Nastavení hlavního okna
        self.root.title("FlatShare Splitter")
        self.root.geometry("800x600")  # Výchozí velikost okna

        # 1. Načtení dat z backendu hned při startu
        print("Načítám data z databáze do GUI...")
        self.household = self.db.load_all_data()

        # 2. Zavoláme metodu, která začne skládat prvky na obrazovku
        self.build_ui()

    def build_ui(self):
        # Smažeme všechno staré a začneme čistě

        # --- ROZDĚLENÍ OKNA NA RÁMEČKY (Frames) ---
        # Levý rámeček (zabere většinu místa, fill=BOTH a expand=YES mu říká, ať se roztáhne)
        left_frame = tb.Frame(self.root, padding=20)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        # Pravý rámeček (bude mít pevnou šířku, roztáhne se jen na výšku přes fill=Y)
        right_frame = tb.Frame(self.root, padding=20)
        right_frame.pack(side=RIGHT, fill=Y)

        # === LEVÁ ČÁST: TABULKA TRANSAKCÍ ===
        # Nadpis levé části
        tb.Label(
            left_frame,
            text="Historie plateb",
            font=("Helvetica", 16, "bold")
        ).pack(anchor=W, pady=(0, 10))  # anchor=W znamená zarovnání doleva (West)

        # Vytvoření samotné tabulky (Treeview)
        columns = ("date", "payer", "amount", "description")
        self.tree = tb.Treeview(left_frame, columns=columns, show="headings", bootstyle=INFO)

        # Nastavení textů v hlavičce
        self.tree.heading("date", text="Datum")
        self.tree.heading("payer", text="Platil")
        self.tree.heading("amount", text="Částka")
        self.tree.heading("description", text="Popis")

        # Nastavení šířky sloupců
        self.tree.column("date", width=120)
        self.tree.column("payer", width=100)
        self.tree.column("amount", width=100, anchor=E)  # anchor=E zarovná čísla doprava
        self.tree.column("description", width=250)

        # Vykreslení tabulky
        self.tree.pack(fill=BOTH, expand=YES)

        # !!! NAPLNĚNÍ TABULKY REÁLNÝMI DATY !!!
        # Tady vytěžíme tvoji skvělou práci na backendu
        for t in self.household.transactions:
            self.tree.insert("", END, values=(
                t.date,
                t.payer.name,  # Vidíš? Saháme přímo do objektu Roommate!
                f"{t.amount:.2f} Kč",  # Formátování na 2 desetinná místa
                t.description
            ))

        # === PRAVÁ ČÁST: PŘEHLED (zatím kostra) ===
        tb.Label(
            right_frame,
            text="Přehled",
            font=("Helvetica", 16, "bold")
        ).pack(anchor=W, pady=(0, 10))

        tb.Label(
            right_frame,
            text=f"Aktivní spolubydlící: {len(self.household.roommates)}"
        ).pack(anchor=W)

        # Zde později přidáme výpis zůstatků a tlačítka "Přidat..."

# Spouštěcí blok
if __name__ == "__main__":
    # Připojíme se k tvojí databázi
    db = DatabaseManager('test_data.db')

    # Vytvoříme hlavní okno.
    # themename můžeš změnit (zkus např. 'lumen', 'darkly', 'superhero', 'flatly')
    root_window = tb.Window(themename="superhero")

    # Vytvoříme instanci naší aplikace a předáme jí okno a databázi
    app = App(root_window, db)

    # Spustíme nekonečnou smyčku okna
    root_window.mainloop()