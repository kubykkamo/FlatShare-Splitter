from models import Roommate, Transaction, Household
from storage import DatabaseManager


def test_flow():
    # 1. Startujeme
    db = DatabaseManager('test_data.db')

    # 2. Vložíme testovací data (můžeš zakomentovat, až to spustíš podruhé)
    r1 = Roommate("Adam", id=None)
    r2 = Roommate("Bára", id=None)
    db.save_roommate(r1)
    db.save_roommate(r2)

    t1 = Transaction(payer=r1, amount=500.0, description="Nákup", involved=[r1, r2])
    db.save_transaction(t1)

    print("--- DATA ULOŽENA DO SQLITE ---")

    # 3. KONTROLA NAČÍTÁNÍ
    # Nejdřív lidi
    loaded_roommates = db.load_all_roommates()
    r_dict = {r.id: r for r in loaded_roommates}

    # Pak transakce
    loaded_transactions = db.load_all_transactions(r_dict)

    print(f"Načteno transakcí: {len(loaded_transactions)}")

    for t in loaded_transactions:
        print(f"Platba: {t.description}")
        print(f"  Platil: {t.payer.name} (objekt typu {type(t.payer)})")
        print(f"  Zúčastnění: {[r.name for r in t.involved]}")

        # HLAVNÍ TEST: Je plátce stejná instance jako v seznamu zúčastněných?
        # V Pythonu operátor 'is' kontroluje, zda jde o stejné místo v paměti
        is_same = t.payer is r_dict[t.payer.id]
        print(f"  Je instance plátce v pořádku? {'ANO' if is_same else 'NE - chyba v logice!'}")


if __name__ == "__main__":
    test_flow()