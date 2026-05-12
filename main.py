
import ttkbootstrap as tb

from storage import DatabaseManager
from gui import App

if __name__ == "__main__":
    # 1. Inicializace databáze
    db = DatabaseManager()

    # 2. Vytvoření hlavního okna
    root = tb.Window(themename="darkly")

    # 3. Předání okna a databáze do gui
    app = App(root, db)

    # 4. Spuštění hlavní nekonečné smyčky
    root.mainloop()