import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime


class App:
    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager

        # Konfigurace hlavního okna aplikace
        self.root.title("FlatShare Splitter")
        self.root.geometry("1280x800")

        # Načtení databáze do paměti při startu (vyhnutí se neustálým dotazům na DB)
        self.show_toast("Načítám data z databáze do GUI...", True)
        self.household = self.db.load_all_data()

        # Prvotní vykreslení rozhraní
        self.build_ui()

    def build_ui(self):
        # Vyčištění okna (nezbytné pro správné překreslení po přidání nových dat)
        for widget in self.root.winfo_children():
            widget.destroy()

        # --- ROZVRŽENÍ LAYOUTU ---
        # Levý panel (dynamicky roztažitelný pro tabulku)
        left_frame = tb.Frame(self.root, padding=20)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        # Pravý panel (fixní šířka pro ovládací prvky)
        right_frame = tb.Frame(self.root, padding=20)
        right_frame.pack(side=RIGHT, fill=Y)

        # === LEVÁ ČÁST: HISTORIE A FILTRY ===
        tb.Label(
            left_frame,
            text="Historie plateb",
            font=("Helvetica", 16, "bold")
        ).pack(anchor=W, pady=(0, 10))

        # Panel pro filtrování podle data
        filter_frame = tb.Frame(left_frame)
        filter_frame.pack(fill=X, pady=(0, 10))

        tb.Label(filter_frame, text="Od:").pack(side=LEFT, padx=(0, 5))
        self.date_from = tb.DateEntry(filter_frame, bootstyle=PRIMARY, dateformat="%d.%m.%Y")
        self.date_from.pack(side=LEFT, padx=(0, 15))

        tb.Label(filter_frame, text="Do:").pack(side=LEFT, padx=(0, 5))
        self.date_to = tb.DateEntry(filter_frame, bootstyle=PRIMARY, dateformat="%d.%m.%Y")
        self.date_to.pack(side=LEFT, padx=(0, 15))

        tb.Button(filter_frame, text="Filtrovat", bootstyle=SECONDARY, command=self.apply_filter).pack(side=LEFT)

        # Definice a konfigurace Treeview (tabulky transakcí)
        columns = ("date", "payer", "amount", "description")
        self.tree = tb.Treeview(left_frame, columns=columns, show="headings", bootstyle=INFO)

        # Binding řadicí logiky na kliknutí do hlavičky sloupce
        self.tree.heading("date", text="Datum", anchor=CENTER, command=lambda: self.sort_treeview("date", False))
        self.tree.heading("payer", text="Platil", anchor=CENTER, command=lambda: self.sort_treeview("payer", False))
        self.tree.heading("amount", text="Částka", anchor=E, command=lambda: self.sort_treeview("amount", False))
        self.tree.heading("description", text="Popis", anchor=CENTER,
                          command=lambda: self.sort_treeview("description", False))

        self.tree.column("date", width=120, anchor=CENTER)
        self.tree.column("payer", width=100, anchor=CENTER)
        self.tree.column("amount", width=100, anchor=E)
        self.tree.column("description", width=250, anchor=CENTER)

        self.tree.pack(fill=BOTH, expand=YES)

        # Populace tabulky daty z doménového modelu
        for t in self.household.transactions:
            if t.date:
                time = datetime.fromisoformat(t.date)
                polished_date = time.strftime("%d.%m.%Y %H:%M")
            else:
                polished_date = "No date"

            self.tree.insert("", END, values=(
                polished_date,
                t.payer.name,
                f"{t.amount:.2f} Kč",
                t.description
            ))

        # === PRAVÁ ČÁST: OVLÁDACÍ PANEL ===
        tb.Label(right_frame, text="Přehled", font=("Helvetica", 16, "bold")).pack(anchor=W, pady=(0, 10))
        tb.Label(right_frame, text=f"Aktivní spolubydlící: {len(self.household.roommates)}").pack(anchor=W)

        tb.Button(right_frame, text="+ Přidat osobu", bootstyle=SUCCESS, command=self.open_add_roommate_dialog).pack(
            pady=10, fill=X)
        tb.Button(right_frame, text="+ Přidat platbu", bootstyle=INFO, command=self.open_add_transaction_dialog).pack(
            pady=10, fill=X)
        tb.Button(right_frame, text="✨ Vypočítat vyrovnání", bootstyle=WARNING,
                  command=self.show_settlement_dialog).pack(pady=30, fill=X)

    def sort_treeview(self, col, reverse):
        """Řadí data v Treeview po kliknutí na hlavičku. Ošetřuje konverzi měny zpět na float."""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        def sort_key(item):
            hodnota = item[0]
            # Extrakce čistého čísla ze stringu pro korektní řazení částek
            if "Kč" in hodnota:
                try:
                    ciste_cislo = hodnota.replace(" Kč", "").replace(" ", "")
                    return float(ciste_cislo)
                except ValueError:
                    return 0.0
            return hodnota.lower()

        l.sort(key=sort_key, reverse=reverse)

        # Fyzické přeskládání iterátorů v GUI
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Invertování směru řazení pro příští kliknutí
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def open_add_transaction_dialog(self):
        """Modální okno pro zadání nové transakce a výběr participujících osob."""
        # Validace stavu: Transakci nelze zadat do prázdné domácnosti
        if not self.household.roommates:
            self.show_toast("Nejdřív přidej aspoň jednoho spolubydlícího!", False)
            return

        dialog = tb.Toplevel(self.root)
        dialog.title("Nová platba")
        dialog.geometry("400x700")

        # 1. Payer selection
        tb.Label(dialog, text="Kdo to platil:").pack(pady=(10, 0))
        jmena_lidi = [r.name for r in self.household.roommates]
        payer_combo = tb.Combobox(dialog, values=jmena_lidi, state="readonly")
        payer_combo.pack(pady=5, padx=20, fill=X)
        payer_combo.current(0)

        # 2. Amount and Description
        tb.Label(dialog, text="Částka (Kč):").pack(pady=(10, 0))
        amount_entry = tb.Entry(dialog)
        amount_entry.pack(pady=5, padx=20, fill=X)

        tb.Label(dialog, text="Za co to bylo (Popis):").pack(pady=(10, 0))
        desc_entry = tb.Entry(dialog)
        desc_entry.pack(pady=5, padx=20, fill=X)

        # 3. Involved selection (Dynamické generování checkboxů podle aktuálních členů)
        tb.Label(dialog, text="Koho se to týká (včetně plátce):").pack(pady=(15, 5))

        checkbox_vars = {}
        for r in self.household.roommates:
            var = tb.BooleanVar(value=False)
            checkbox_vars[r.id] = var
            tb.Checkbutton(dialog, text=r.name, variable=var, bootstyle="round-toggle").pack(anchor=W, padx=40, pady=2)

        def save_transaction():
            vybrane_jmeno = payer_combo.get()
            popis = desc_entry.get().strip()

            # Validace vstupu částky
            try:
                castka = float(amount_entry.get().strip())
            except ValueError:
                self.show_toast("Chyba: Částka musí být číslo!", False)
                return

            platce_objekt = next((r for r in self.household.roommates if r.name == vybrane_jmeno), None)

            # Filtrování zaškrtnutých osob přes vyhodnocení stavu boolean proměnných
            zapojeni_lidi = [r for r in self.household.roommates if checkbox_vars[r.id].get() == True]

            if platce_objekt and castka > 0 and zapojeni_lidi and popis:
                from models import Transaction
                time = datetime.now().isoformat()

                nova_platba = Transaction(
                    id=None, payer=platce_objekt, amount=castka,
                    description=popis, date=time, involved=zapojeni_lidi
                )

                # Persistence dat a aktualizace stavu aplikace
                self.db.save_transaction(nova_platba)
                self.household = self.db.load_all_data()
                self.build_ui()
                dialog.destroy()
                self.show_toast("Platba uložena!", True)
            else:
                self.show_toast("Chybně zadané údaje!", False)

        tb.Button(dialog, text="Uložit platbu", bootstyle=SUCCESS, command=save_transaction).pack(pady=20)

    def apply_filter(self):
        """Aplikuje časový filtr na lokální instanci načtených dat."""
        date_from_str = self.date_from.entry.get()
        date_to_str = self.date_to.entry.get()

        from datetime import datetime
        try:
            start_date = datetime.strptime(date_from_str, "%d.%m.%Y")
            # Koncové datum prodlouženo na konec dne pro zachycení večerních transakcí
            end_date = datetime.strptime(date_to_str, "%d.%m.%Y").replace(hour=23, minute=59, second=59)
        except ValueError:
            self.show_toast("Špatný formát data v kalendáři.", False)
            return

        # Vytvoření dočasného listu pro vyfiltrované záznamy
        self.displayed_transactions = []
        for t in self.household.transactions:
            if t.date:
                tx_date = datetime.fromisoformat(t.date)
                if start_date <= tx_date <= end_date:
                    self.displayed_transactions.append(t)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for t in self.displayed_transactions:
            skutecny_cas = datetime.fromisoformat(t.date)
            hezke_datum = skutecny_cas.strftime("%d.%m.%Y %H:%M")
            self.tree.insert("", "end", values=(hezke_datum, t.payer.name, f"{t.amount:.2f} Kč", t.description))

    def show_settlement_dialog(self):
        """Vyhodnocení dluhů a zobrazení návrhu vyrovnání. Zohledňuje případný aktivní filtr."""

        # Fallback mechanismus: použije se filtrovaný dataset, pokud existuje, jinak primární
        txs_to_calculate = getattr(self, 'displayed_transactions', self.household.transactions)
        settlements = self.household.calculate_settlement(txs_to_calculate)

        dialog = tb.Toplevel(self.root)
        dialog.title("Konečné vyrovnání")
        dialog.geometry("400x500")

        tb.Label(dialog, text="Kdo komu dluží?", font=("Helvetica", 16, "bold")).pack(pady=20)

        if not settlements:
            tb.Label(dialog, text="Všichni jsou vyrovnaní! 🎉", font=("Helvetica", 12), bootstyle=SUCCESS).pack(pady=20)
        else:
            for debtor, creditor, amount in settlements:
                vysledny_text = f"{debtor.name} ➔ pošle ➔ {creditor.name}: {amount:.2f} Kč"
                tb.Label(dialog, text=vysledny_text, font=("Helvetica", 12, "bold"), bootstyle=DANGER).pack(pady=10)

        tb.Button(dialog, text="Zavřít", bootstyle=SECONDARY, command=dialog.destroy).pack(pady=30)

    def open_add_roommate_dialog(self):
        dialog = tb.Toplevel(self.root)
        dialog.title("Nový spolubydlící")
        dialog.geometry("300x150")

        tb.Label(dialog, text="Jméno spolubydlícího:").pack(pady=(10, 5))
        name_entry = tb.Entry(dialog)
        name_entry.pack(pady=5, padx=20, fill=X)

        def save_data():
            name = name_entry.get().strip()
            if name:
                from models import Roommate
                novy_clovek = Roommate(name=name, id=None)

                # Zápis do DB a synchronizace in-memory dat
                self.db.save_roommate(novy_clovek)
                self.household = self.db.load_all_data()
                self.build_ui()
                dialog.destroy()
                self.show_toast(f"Spolubydlící '{name}' uložen!", True)
            else:
                self.show_toast("Zadej jméno nového spolubydlícího!", False)

        tb.Button(dialog, text="Uložit", bootstyle=PRIMARY, command=save_data).pack(pady=10)

    def show_toast(self, message: str, success: bool):
        """Asynchronní UI notifikace (tzv. Toast) s automatickým zničením po 3 sekundách."""
        style = "success" if success else "danger"

        toast_label = tb.Label(
            self.root,
            text=message,
            bootstyle=f"inverse-{style}",
            padding=10,
            font=("Helvetica", 10, "bold")
        )

        # Centrování přes relativní souřadnice
        toast_label.place(relx=0.5, rely=0.9, anchor="center")
        self.root.after(3000, toast_label.destroy)