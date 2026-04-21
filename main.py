from models import Roommate, Transaction, Household
from storage import DatabaseManager

# 1. Vytvoření spolubydlících
"""

vsichni = [adam, bara, cyril, dan]

# 2. Inicializace domácnosti a přidání lidí
domacnost = Household()
for r in vsichni:
    domacnost.add_roommate(r)

# 3. Generování 10 různorodých plateb
transakce = [
    # Velký nákup pro všechny
    Transaction(payer=adam, amount=1200, description="Velký nákup (Tesco)", involved=vsichni),

    # Bára platí internet pro všechny
    Transaction(payer=bara, amount=500, description="Internet na měsíc", involved=vsichni),

    # Cyril koupil piva, ale Dan nepije, takže se dělí jen 3 lidé
    Transaction(payer=cyril, amount=330, description="Piva na večer", involved=[adam, bara, cyril]),

    # Dan zaplatil nedoplatek za elektřinu
    Transaction(payer=dan, amount=800, description="Nedoplatek elektřina", involved=vsichni),

    # Adam koupil čistící prostředky (pro všechny)
    Transaction(payer=adam, amount=150, description="Savo, hadry", involved=vsichni),

    # Bára objednala pizzu jen pro sebe a Dana
    Transaction(payer=bara, amount=440, description="Pizza (Bára + Dan)", involved=[bara, dan]),

    # Cyril koupil společný dárek pro kamaráda (skládali se všichni kromě Cyrila)
    Transaction(payer=cyril, amount=600, description="Dárek pro Honzu", involved=[adam, bara, dan]),

    # Dan platí Netflix, používají ho jen on a Adam
    Transaction(payer=dan, amount=320, description="Netflix", involved=[adam, dan]),

    # Adam platí společnou večeři, ale sám nejedl (dělí se Bára, Cyril, Dan)
    Transaction(payer=adam, amount=900, description="Večeře v hospodě", involved=[bara, cyril, dan]),

    # Bára vzala auto na výlet, platí benzín pro všechny
    Transaction(payer=bara, amount=1000, description="Benzín na výlet", involved=vsichni),
]

# Přidání transakcí do domácnosti
for t in transakce:
    domacnost.add_transaction(t)

# --- VÝPISY PRO KONTROLU ---

print("=== 1. KROK: ČISTÉ ZŮSTATKY ===")
balances = domacnost.calculate_balances()
for roommate, balance in balances.items():
    if balance > 0:
        print(f"{roommate.name} je v plusu: +{balance} Kč (Věřitel)")
    elif balance < 0:
        print(f"{roommate.name} je v mínusu: {balance} Kč (Dlužník)")
    else:
        print(f"{roommate.name} je přesně na nule.")

print("\n=== 2. KROK: KONEČNÉ VYROVNÁNÍ (Kdo komu pošle) ===")
settlements = domacnost.calculate_settlement()

celkem_transakci = 0
for debtor, creditor, amount in settlements:
    print(f"💸 {debtor.name} pošle {amount} Kč uživateli {creditor.name}")
    celkem_transakci += 1

print(f"\nZe 10 účtenek jsme udělali pouze {celkem_transakci} bankovních převodů!")

"""





