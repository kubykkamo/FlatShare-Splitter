from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Roommate:
    name: str
    id: Optional[int] = None  # ID se bude hodit později pro propojení s databází

    def __hash__(self):
        # Abychom mohli Roommate používat jako klíče ve slovníku
        return hash((self.id, self.name))

    def __eq__(self, other):
        if not isinstance(other, Roommate):
            return False
        # Pokud mají ID, porovnáváme podle ID (z DB), jinak podle jména
        if self.id and other.id:
            return self.id == other.id
        return self.name == other.name

@dataclass
class Transaction:
    payer: Roommate
    amount: float
    description: str
    involved: List[Roommate]
    date: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None

class Household:
    """
    Hlavní doménová třída spravující stav a logiku výpočtů.
    """
    def __init__(self):
        self.roommates: List[Roommate] = []
        self.transactions: List[Transaction] = []

    def load_data(self, roommates: List[Roommate], transactions: List[Transaction]):
        """Pomocná metoda pro prvotní naplnění daty ze storage."""
        self.roommates = roommates
        self.transactions = transactions

    def add_roommate(self, roommate: Roommate):
        if roommate not in self.roommates:
            self.roommates.append(roommate)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def calculate_balances(self) -> Dict[Roommate, float]:
        """
        Vypočítá aktuální čistý zůstatek každého spolubydlícího.
        Kladné číslo = ostatní mu dluží (věřitel).
        Záporné číslo = on dluží ostatním (dlužník).
        """
        # Inicializace zůstatků na 0.0
        balances = {r: 0.0 for r in self.roommates}

        for t in self.transactions:
            # 1. Plátci přičteme celou částku, kterou zaplatil (je v plusu)
            if t.payer in balances:
                balances[t.payer] += t.amount

            # 2. Všem zúčastněným (včetně plátce, pokud se účastní) odečteme jejich podíl
            if t.involved:
                split_amount = t.amount / len(t.involved)
                for r in t.involved:
                    if r in balances:
                        balances[r] -= split_amount

        # Zaokrouhlíme na 2 desetinná místa, abychom se vyhnuli float nepřesnostem (např. 0.00000000001)
        return {r: round(bal, 2) for r, bal in balances.items()}

    def calculate_settlement(self) -> List[Tuple[Roommate, Roommate, float]]:
        """
        Vypočítá minimální počet transakcí pro vyrovnání dluhů.
        Vrací list tuplů ve formátu: (Kdo_posílá, Komu_posílá, Částka)
        """
        balances = self.calculate_balances()

        # Rozdělíme lidi na dlužníky a věřitele
        # Ukládáme jako [Roommate, částka] (částku si u dlužníků převedeme na absolutní hodnotu)
        debtors = [[r, abs(bal)] for r, bal in balances.items() if bal < -0.01]
        creditors = [[r, bal] for r, bal in balances.items() if bal > 0.01]

        # Seřadíme sestupně podle velikosti dluhu/pohledávky pro mírnou optimalizaci
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)

        settlements = []

        i = 0  # Ukazatel pro dlužníky
        j = 0  # Ukazatel pro věřitele

        while i < len(debtors) and j < len(creditors):
            debtor, debt_amount = debtors[i]
            creditor, credit_amount = creditors[j]

            # Vyrovnáme maximum možného mezi těmito dvěma
            settle_amount = min(debt_amount, credit_amount)
            settle_amount = round(settle_amount, 2)

            if settle_amount > 0:
                settlements.append((debtor, creditor, settle_amount))

            # Aktualizujeme zbývající částky
            debtors[i][1] = round(debt_amount - settle_amount, 2)
            creditors[j][1] = round(credit_amount - settle_amount, 2)

            # Pokud má dlužník splaceno, posuneme se na dalšího
            if debtors[i][1] <= 0:
                i += 1
            # Pokud je věřitel uspokojen, posuneme se na dalšího
            if creditors[j][1] <= 0:
                j += 1

        return settlements

