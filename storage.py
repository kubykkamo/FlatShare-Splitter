import sqlite3
from models import Roommate, Transaction

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

