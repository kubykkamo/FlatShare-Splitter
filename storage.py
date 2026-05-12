import sqlite3
from models import Roommate, Transaction, Household


class DatabaseManager:
    def __init__(self, db_path: str = 'test_data.db'):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Vytvoří spojení a vynutí kontrolu cizích klíčů (SQLite je má v základu vypnuté)."""
        conn = sqlite3.connect(self.db_path)
        # Nastavení, aby databáze vracela řádky jako slovníky (dá se k nim přistupovat přes klíče)
        conn.row_factory = sqlite3.Row
        # Nutné pro fungování ON DELETE CASCADE
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Příprava tabulek při úplně prvním spuštění aplikace."""
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

            # Vazební tabulka (kdo všechno se podílel na dané útratě)
            c.execute("""
                      CREATE TABLE IF NOT EXISTS transaction_involved (
                  transaction_id INTEGER
                  NOT NULL,
                  roommate_id INTEGER NOT NULL,
                  PRIMARY KEY(transaction_id,roommate_id),
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
            # Uložení přiděleného primárního klíče zpět do objektu
            roommate.id = c.lastrowid
            print(f"{roommate.name} saved with id {roommate.id}.")

    def load_all_roommates(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM roommates")

            data = c.fetchall()
            roommates = []

            for item in data:
                roommate = Roommate(name=item['name'], id=item['id'])
                # print(f"{roommate.name} loaded with id {roommate.id}.")  # debug
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

            # Zápis do vazební tabulky pro každého, koho se platba týkala
            for roommate in transaction.involved:
                c.execute(
                    "INSERT INTO transaction_involved (transaction_id, roommate_id) VALUES (?, ?)",
                    (transaction.id, roommate.id)
                )

    def load_all_transactions(self, roommates_dict):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM transactions t")

            data = c.fetchall()
            transactions = []

            for item in data:
                # Dohledání objektu plátce přes dictionary (rychlejší než dělat další JOIN v SQL)
                p_id = item['payer_id']
                payer_object = roommates_dict[p_id]

                current_transaction_id = item['id']

                # Vytažení všech lidí zapojených do této konkrétní transakce
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

    def load_all_data(self):
        all_roommates = self.load_all_roommates()

        # Vytvoření slovníku {id: objekt} pro rychlejší párování transakcí s lidmi při načítání
        r_dict = {r.id: r for r in all_roommates}

        all_transactions = self.load_all_transactions(r_dict)

        household = Household()
        household.roommates = all_roommates
        household.transactions = all_transactions

        return household