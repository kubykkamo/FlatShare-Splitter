import sqlite3
from models import Roommate, Transaction, Household


class DatabaseManager:
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Vytvoří připojení a bezpečně zapne cizí klíče."""
        conn = sqlite3.connect(self.db_path)
        # SQLite specifikum: pro interpretaci row objektů jako slovníků (lepší práce s daty)
        conn.row_factory = sqlite3.Row
        # Zásadní zapnutí kaskádování a cizích klíčů
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Vytvoří tabulky, pokud ještě neexistují."""

        with self.get_connection() as conn:
            c = conn.cursor()

            c.execute("""
                CREATE TABLE IF NOT EXISTS roommates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payer_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (payer_id) REFERENCES roommates(id)
                );
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS transaction_involved (
                    transaction_id INTEGER NOT NULL,
                    roommate_id INTEGER NOT NULL,
                    PRIMARY KEY (transaction_id, roommate_id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                    FOREIGN KEY (roommate_id) REFERENCES roommates(id) ON DELETE CASCADE
                );
            """)

    def save_roommate(self, roommate):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO roommates (name) VALUES (?)",
                (roommate.name,)
            )

            roommate.id = c.lastrowid
            print(f"{roommate.name} saved with id {roommate.id}.")


    def load_all_roommates(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM roommates")

            data = c.fetchall()
            roommates = []

            for item in data:
                roommate = Roommate(name=item['name'], id=item['id'])
                # print(f"{roommate.name} loaded with id {roommate.id}.")
                roommates.append(roommate)


            return roommates

    def save_transaction(self, transaction):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO transactions (payer_id, amount, description, created_at) VALUES (?, ?, ?, ?)",
                (transaction.payer.id, transaction.amount, transaction.description, transaction.date)
            )

            transaction.id = c.lastrowid
            # inserting record for every roommate involved in transaction
            for roommate in transaction.involved:
                c.execute(
                    "INSERT INTO transaction_involved (transaction_id, roommate_id) VALUES (?, ?)",
                    (transaction.id, roommate.id)
                )


    def load_all_transactions(self, roommates_dict):

        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM transactions t"
            )

            data = c.fetchall()
            transactions = []
            for item in data:
                p_id = item['payer_id']
                payer_object = roommates_dict[p_id]

                current_transaction_id = item['id']

                c.execute(
                    "SELECT roommate_id FROM transaction_involved WHERE transaction_id = ?",
                    (current_transaction_id,)
                )

                involved_list = []
                inv_data = c.fetchall()
                for inv_item in inv_data:
                    i_id = inv_item['roommate_id']
                    involved_object = roommates_dict[i_id]
                    involved_list.append(involved_object)

                t = Transaction(
                    id=item['id'],
                    payer=payer_object,
                    amount=item['amount'],
                    description=item['description'],
                    date=item['created_at'],
                    involved=involved_list

                )


                transactions.append(t)
        return transactions
    