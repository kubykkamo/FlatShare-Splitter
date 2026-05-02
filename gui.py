import ttkbootstrap as tb
from ttkbootstrap.constants import *
from storage import DatabaseManager
from datetime import datetime

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
        for widget in self.root.winfo_children():
            widget.destroy()
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
        self.tree.heading("date", text="Datum", anchor=CENTER)
        self.tree.heading("payer", text="Platil", anchor=CENTER)
        self.tree.heading("amount", text="Částka", anchor=E)
        self.tree.heading("description", text="Popis", anchor=CENTER)

        # Nastavení šířky sloupců
        self.tree.column("date", width=120, anchor=CENTER)
        self.tree.column("payer", width=100, anchor=CENTER)
        self.tree.column("amount", width=100, anchor=E )  # anchor=E zarovná čísla doprava
        self.tree.column("description", width=250, anchor=CENTER)

        # Vykreslení tabulky
        self.tree.pack(fill=BOTH, expand=YES)

        # !!! NAPLNĚNÍ TABULKY REÁLNÝMI DATY !!!
        # Tady vytěžíme tvoji skvělou práci na backendu
        for t in self.household.transactions:

            time = datetime.fromisoformat(t.date)

            polished_date = time.strftime("%d.%m.%Y %H:%M")

            self.tree.insert("", END ,values=(
                polished_date,
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

        tb.Button(
            right_frame,
            text="+ Přidat osobu",
            bootstyle=SUCCESS,  # Zelené tlačítko
            command=self.open_add_roommate_dialog  # Tady říkáme, co se má stát po kliknutí
        ).pack(pady=10, fill=X)

        # Zde později přidáme výpis zůstatků a tlačítka "Přidat..."

    def open_add_roommate_dialog(self):
        # Vytvoření nového okna na popředí (Toplevel)
        dialog = tb.Toplevel(self.root)
        dialog.title("Nový spolubydlící")
        dialog.geometry("300x150")

        # Nápis a textové pole
        tb.Label(dialog, text="Jméno spolubydlícího:").pack(pady=(10, 5))
        name_entry = tb.Entry(dialog)
        name_entry.pack(pady=5, padx=20, fill=X)

        # Vnitřní funkce, která odpracuje uložení
        def save_data():
            # Získáme text z pole a odstraníme mezery na okrajích
            name = name_entry.get().strip()

            if name:  # Pokud uživatel něco napsal (není to prázdné)
                from models import Roommate  # Importujeme si tvůj model

                # 1. Vytvoříme objekt (ID necháme None, databáze si ho vygeneruje)
                novy_clovek = Roommate(name=name, id=None)

                # 2. Pošleme ho do tvé hotové databázové metody
                self.db.save_roommate(novy_clovek)

                # 3. Znovu načteme celou databázi do paměti
                self.household = self.db.load_all_data()

                # 4. Překreslíme celou obrazovku, ať je to hned vidět!
                self.build_ui()

                # 5. Zavřeme vyskakovací okno
                dialog.destroy()

        # Tlačítko, které to celé spustí
        tb.Button(dialog, text="Uložit", bootstyle=PRIMARY, command=save_data).pack(pady=10)

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