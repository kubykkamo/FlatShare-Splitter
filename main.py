from models import Roommate, Transaction, Household
from storage import DatabaseManager

db = DatabaseManager()
db.get_connection()

roommates = db.load_all_roommates()

household = Household()

for r in roommates:
    household.add_roommate(r)

adam = household.roommates[1]

transaction = Transaction(payer = household.roommates[0], amount = 500, description='Nakup', involved=[adam])

household.add_transaction(Transaction(payer=household.roommates[1], amount=500, description='Nakup', involved=[household.roommates[0], household.roommates[2]]))

household.add_transaction(transaction)

db.save_transaction(transaction)


