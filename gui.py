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

        # === FILTROVACÍ LIŠTA ===
        filter_frame = tb.Frame(left_frame)
        filter_frame.pack(fill=X, pady=(0, 10))

        tb.Label(filter_frame, text="Od:").pack(side=LEFT, padx=(0, 5))
        # Kalendář pro počáteční datum (s vynuceným českým formátem)
        self.date_from = tb.DateEntry(filter_frame, bootstyle=PRIMARY, dateformat="%d.%m.%Y")
        self.date_from.pack(side=LEFT, padx=(0, 15))

        tb.Label(filter_frame, text="Do:").pack(side=LEFT, padx=(0, 5))
        # Kalendář pro koncové datum
        self.date_to = tb.DateEntry(filter_frame, bootstyle=PRIMARY, dateformat="%d.%m.%Y")
        self.date_to.pack(side=LEFT, padx=(0, 15))

        # Tlačítko, které zatím nic nedělá, ale brzy bude spouštět filtrování
        # V metodě build_ui uprav tlačítko "Filtrovat" takto:
        tb.Button(filter_frame, text="Filtrovat", bootstyle=SECONDARY, command=self.apply_filter).pack(side=LEFT)

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

            if t.date:
                time = datetime.fromisoformat(t.date)

                polished_date = time.strftime("%d.%m.%Y %H:%M")
            else:
                polished_date = "No date"
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

        # Tlačítko pro přidání platby (dáme mu jinou barvu, třeba modrou - INFO)
        tb.Button(
            right_frame,
            text="+ Přidat platbu",
            bootstyle=INFO,
            command=self.open_add_transaction_dialog
        ).pack(pady=10, fill=X)

        # Tlačítko pro spuštění výpočtu vyrovnání
        tb.Button(
            right_frame,
            text="✨ Vypočítat vyrovnání",
            bootstyle=WARNING,
            command=self.show_settlement_dialog
        ).pack(pady=30, fill=X)  # pady=30 ho trochu víc oddělí od ostatních

    def open_add_transaction_dialog(self):
        # Ochrana: Nesmíme přidávat platbu, když v bytě nikdo nebydlí
        if not self.household.roommates:
            print("Nejdřív přidej aspoň jednoho spolubydlícího!")
            return

        dialog = tb.Toplevel(self.root)
        dialog.title("Nová platba")
        dialog.geometry("400x550")

        # 1. KDO PLATIL (Roletka / Combobox)
        tb.Label(dialog, text="Kdo to platil:").pack(pady=(10, 0))
        # Vytáhneme si jen jména lidí do seznamu pro roletku
        jmena_lidi = [r.name for r in self.household.roommates]
        payer_combo = tb.Combobox(dialog, values=jmena_lidi, state="readonly")
        payer_combo.pack(pady=5, padx=20, fill=X)
        payer_combo.current(0)  # Nastavíme výchozího prvního člověka

        # 2. ČÁSTKA A POPIS
        tb.Label(dialog, text="Částka (Kč):").pack(pady=(10, 0))
        amount_entry = tb.Entry(dialog)
        amount_entry.pack(pady=5, padx=20, fill=X)

        tb.Label(dialog, text="Za co to bylo (Popis):").pack(pady=(10, 0))
        desc_entry = tb.Entry(dialog)
        desc_entry.pack(pady=5, padx=20, fill=X)

        # 3. KDO SE PODÍLÍ (Generování Checkboxů)
        tb.Label(dialog, text="Koho se to týká (včetně plátce):").pack(pady=(15, 5))

        # Tady si schováme proměnné checkboxů. Klíč bude ID člověka, hodnota stav (True/False)
        checkbox_vars = {}
        for r in self.household.roommates:
            var = tb.BooleanVar(value=True)  # Ve výchozím stavu zaškrtneme všechny
            checkbox_vars[r.id] = var
            # bootstyle="round-toggle" udělá místo nudného čtverečku hezký přepínač
            tb.Checkbutton(dialog, text=r.name, variable=var, bootstyle="round-toggle").pack(anchor=W, padx=40, pady=2)

        # Vnitřní funkce pro uložení
        def save_transaction():
            vybrane_jmeno = payer_combo.get()
            popis = desc_entry.get().strip()

            # Bezpečnostní kontrola, jestli uživatel nenapsal místo čísla text
            try:
                castka = float(amount_entry.get().strip())
            except ValueError:
                print("Chyba: Částka musí být číslo!")
                return

                # Najdeme reálný objekt plátce podle vybraného jména
            platce_objekt = next((r for r in self.household.roommates if r.name == vybrane_jmeno), None)

            # Posbíráme zaškrtnuté lidi
            zapojeni_lidi = []
            for r in self.household.roommates:
                # Zkontrolujeme, jestli je checkbox pro tohle ID zaškrtnutý (get() vrací True/False)
                if checkbox_vars[r.id].get() == True:
                    zapojeni_lidi.append(r)

            # Pokud máme všechno podstatné, uložíme to
            if platce_objekt and castka > 0 and zapojeni_lidi and popis:
                from models import Transaction
                # Vytvoříme novou transakci. ID a datum si vygeneruje databáze

                time = datetime.now().isoformat()

                # Předáme ho místo None
                nova_platba = Transaction(
                    id=None, payer=platce_objekt, amount=castka,
                    description=popis, date=time, involved=zapojeni_lidi
                )

                # Uložení a překreslení (stejný postup jako u osoby)
                self.db.save_transaction(nova_platba)
                self.household = self.db.load_all_data()
                self.build_ui()
                dialog.destroy()
            else:
                print("Chyba: Nevyplnil jsi všechny údaje (nebo jsi nevybral žádné lidi).")

        # Ukládací tlačítko
        tb.Button(dialog, text="Uložit platbu", bootstyle=SUCCESS, command=save_transaction).pack(pady=20)

    def apply_filter(self):
        date_from_str = self.date_from.entry.get()
        date_to_str = self.date_to.entry.get()

        from datetime import datetime
        try:
            # Převedeme text z kalendáře na opravdový čas
            start_date = datetime.strptime(date_from_str, "%d.%m.%Y")
            # U koncového data nastavíme čas na 23:59:59, ať to vezme i platby z toho večera
            end_date = datetime.strptime(date_to_str, "%d.%m.%Y").replace(hour=23, minute=59, second=59)
        except ValueError:
            print("Špatný formát data v kalendáři.")
            return

        # 1. Vytvoříme si nový, vyfiltrovaný list plateb
        self.displayed_transactions = []
        for t in self.household.transactions:
            if t.date:
                tx_date = datetime.fromisoformat(t.date)
                if start_date <= tx_date <= end_date:
                    self.displayed_transactions.append(t)

        # 2. Vymažeme staré řádky v tabulce (get_children vrátí ID všech řádků)
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 3. Naplníme tabulku jen vyfiltrovanými platbami
        for t in self.displayed_transactions:
            skutecny_cas = datetime.fromisoformat(t.date)
            hezke_datum = skutecny_cas.strftime("%d.%m.%Y %H:%M")
            self.tree.insert("", "end", values=(hezke_datum, t.payer.name, f"{t.amount:.2f} Kč", t.description))

    def show_settlement_dialog(self):
        # Trik: Zkusíme vzít vyfiltrované platby. Pokud uživatel ještě neklikl na "Filtrovat"
        # (takže proměnná neexistuje), vezmeme záchrannou brzdu a použijeme všechny platby.
        txs_to_calculate = getattr(self, 'displayed_transactions', self.household.transactions)

        # Předáme ten konkrétní list do tvého backendu
        settlements = self.household.calculate_settlement(txs_to_calculate)

        # 2. Vykreslení okna
        dialog = tb.Toplevel(self.root)
        dialog.title("Konečné vyrovnání")
        dialog.geometry("400x500")

        tb.Label(dialog, text="Kdo komu dluží?", font=("Helvetica", 16, "bold")).pack(pady=20)

        # 3. Zpracování tvých dat do UI
        if not settlements:
            tb.Label(dialog, text="Všichni jsou vyrovnaní! 🎉", font=("Helvetica", 12), bootstyle=SUCCESS).pack(pady=20)
        else:
            # Rozbalíme tvůj Tuple (debtor, creditor, amount) přímo v cyklu
            for debtor, creditor, amount in settlements:
                # Tady si GUI rozhoduje, jak to chce vypsat
                vysledny_text = f"{debtor.name} ➔ pošle ➔ {creditor.name}: {amount:.2f} Kč"

                tb.Label(dialog, text=vysledny_text, font=("Helvetica", 12, "bold"), bootstyle=DANGER).pack(pady=10)

        tb.Button(dialog, text="Zavřít", bootstyle=SECONDARY, command=dialog.destroy).pack(pady=30)

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