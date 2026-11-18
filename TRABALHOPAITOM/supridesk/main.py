import tkinter as tk

from supridesk.database import Database
from supridesk.services import SolicitacaoService
from supridesk.ui import App


def main() -> None:
    db = Database("solicitacoes.db")
    service = SolicitacaoService(db)
    root = tk.Tk()
    App(root, service)
    root.mainloop()


if __name__ == "__main__":
    main()
