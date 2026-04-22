from models import Roommate, Transaction, Household
from storage import DatabaseManager


def test_flow():
    # 1. Startujeme
    db = DatabaseManager('data.db')

    household = db.load_all_data()

    settlements = household.calculate_settlement()

    print(settlements)
if __name__ == "__main__":
    test_flow()