from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Roommate:
    name: str
    id: Optional[int] = None  # Primární klíč z DB

    def __hash__(self):
        # Nutné pro fungování Roommate jako klíče v dictu (např. v balances)
        return hash((self.id, self.name))

    def __eq__(self, other):
        if not isinstance(other, Roommate):
            return False
        # Fallback na jméno, pokud ještě objekt nemá ID z databáze
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
    Třída zapouzdřující logiku výpočtů dluhů a správu dat v paměti.
    """
    def __init__(self):
        self.roommates: List[Roommate] = []
        self.transactions: List[Transaction] = []

    def load_data(self, roommates: List[Roommate], transactions: List[Transaction]):
        """Inicializace dat načtených z databáze."""
        self.roommates = roommates
        self.transactions = transactions

    def add_roommate(self, roommate: Roommate):
        if roommate not in self.roommates:
            self.roommates.append(roommate)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def calculate_balances(self, transactions_list=None) -> Dict[Roommate, float]:
        # Zpracuje buď vyfiltrovaný list (pro konkrétní časový úsek) nebo všechny transakce
        txs = transactions_list if transactions_list is not None else self.transactions

        balances = {r: 0.0 for r in self.roommates}

        for t in txs:
            if t.payer in balances:
                balances[t.payer] += t.amount

            if t.involved:
                split_amount = t.amount / len(t.involved)
                for r in t.involved:
                    if r in balances:
                        balances[r] -= split_amount

        return {r: round(bal, 2) for r, bal in balances.items()}

    def calculate_settlement(self, transactions_list=None) -> List[Tuple[Roommate, Roommate, float]]:
        """
        Greedy algoritmus pro minimalizaci počtu transakcí při závěrečném vyrovnání.
        Vrací: list[(Kdo_posílá, Komu_posílá, Částka)]
        """
        balances = self.calculate_balances(transactions_list)

        # Rozdělení na dlužníky (záporný balance) a věřitele (kladný balance)
        debtors = [[r, abs(bal)] for r, bal in balances.items() if bal < -0.01]
        creditors = [[r, bal] for r, bal in balances.items() if bal > 0.01]

        # Seřazení od největších částek pro efektivnější párování (minimalizace počtu transakcí)
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)

        settlements = []
        i, j = 0, 0

        while i < len(debtors) and j < len(creditors):
            debtor, debt_amount = debtors[i]
            creditor, credit_amount = creditors[j]

            # Spárujeme co největší možnou částku mezi těmito dvěma
            settle_amount = round(min(debt_amount, credit_amount), 2)

            if settle_amount > 0:
                settlements.append((debtor, creditor, settle_amount))

            # Odečtení vyrovnané částky ze zbývajícího dluhu/pohledávky
            debtors[i][1] = round(debt_amount - settle_amount, 2)
            creditors[j][1] = round(credit_amount - settle_amount, 2)

            # Posun na další osobu, pokud má dotyčný srovnáno na nulu
            if debtors[i][1] <= 0:
                i += 1
            if creditors[j][1] <= 0:
                j += 1

        return settlements