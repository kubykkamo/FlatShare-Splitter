from models import Roommate, Transaction, Household
from storage import DatabaseManager


def test_flow():
    # 1. Startujeme
    db = DatabaseManager('test_data.db')

    household = db.load_all_data()

    print(household.calculate_settlement())

    for t in household.transactions:
        print(t.description)

if __name__ == "__main__":
    test_flow()