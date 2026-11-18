import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from .services import (ATENDIDA, EM_ATENDIMENTO, PENDENTE, PRIORIDADES,
                       STATUS_LISTA, SolicitacaoService, SupriDeskError)

TODOS = "Todos"


class App(ttk.Frame):
    """Janela principal: só coleta dados e exibe mensagens (sem SQL e sem regras)."""

    def __init__(self, master: tk.Tk, service: SolicitacaoService):
        super().__init__(master, padding=12)
        self.service = service
        self.master.title("SupriDesk — Gestão de Solicitações de Materiais")
        self.master.minsize(900, 560)
        self.pack(fill="both", expand=True)

        self.var_setor = tk.StringVar()
        self.var_material = tk.StringVar()
        self.var_quantidade = tk.StringVar()
        self.var_prioridade = tk.StringVar(value=PRIORIDADES[0])
        self.var_busca = tk.StringVar()
        self.var_filtro = tk.StringVar(value=TODOS)
        self.var_info = tk.StringVar()

        self._montar_formulario()
        self._montar_busca()
        self._montar_tabela()
        self._montar_acoes()
        ttk.Label(self, textvariable=self.var_info, anchor="w").pack(
            fill="x", pady=(8, 0))
        self.atualizar_tabela()

    def _montar_formulario(self):
        box = ttk.LabelFrame(self, text="Nova solicitação", padding=10)
        box.pack(fill="x")

        ttk.Label(box, text="Setor:").grid(row=0, column=0, sticky="w")
        self.ent_setor = ttk.Entry(box, textvariable=self.var_setor, width=22)
        self.ent_setor.bind("<Return>", lambda _e: self.cadastrar())
        self.ent_setor.grid(row=0, column=1, padx=(4, 12))

        ttk.Label(box, text="Material:").grid(row=0, column=2, sticky="w")
        ent_mat = ttk.Entry(box, textvariable=self.var_material, width=26)
        ent_mat.grid(row=0, column=3, padx=(4, 12))
        ent_mat.bind("<Return>", lambda _e: self.cadastrar())

        ttk.Label(box, text="Quantidade:").grid(row=0, column=4, sticky="w")
        ent_qtd = ttk.Entry(box, textvariable=self.var_quantidade, width=8)
        ent_qtd.grid(row=0, column=5, padx=(4, 12))
        ent_qtd.bind("<Return>", lambda _e: self.cadastrar())

        ttk.Label(box, text="Prioridade:").grid(row=0, column=6, sticky="w")
        ttk.Combobox(box, textvariable=self.var_prioridade, values=PRIORIDADES,
                     state="readonly", width=9).grid(row=0, column=7, padx=(4, 12))

        ttk.Button(box, text="Cadastrar", command=self.cadastrar).grid(
            row=0, column=8)

    def _montar_busca(self):
        box = ttk.LabelFrame(self, text="Pesquisa e filtros", padding=10)
        box.pack(fill="x", pady=10)

        ttk.Label(box, text="Setor ou Material:").grid(row=0, column=0)
        ent = ttk.Entry(box, textvariable=self.var_busca, width=30)
        ent.grid(row=0, column=1, padx=(4, 12))
        ent.bind("<Return>", lambda _e: self.atualizar_tabela())

        ttk.Label(box, text="Status:").grid(row=0, column=2)
        cb = ttk.Combobox(
            box, textvariable=self.var_filtro, state="readonly",
            values=[TODOS] + STATUS_LISTA, width=16)
        cb.grid(row=0, column=3, padx=(4, 12))
        cb.bind("<<ComboboxSelected>>", lambda _e: self.atualizar_tabela())

        ttk.Button(box, text="Pesquisar", command=self.atualizar_tabela).grid(
            row=0, column=4, padx=4)
        ttk.Button(box, text="Limpar filtros", command=self.limpar_filtros).grid(
            row=0, column=5, padx=4)

    def _montar_tabela(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)

        colunas = [("id", "Nº", 50), ("setor", "Setor", 140),
                   ("material", "Material", 200), ("quantidade", "Qtd", 60),
                   ("prioridade", "Prioridade", 90), ("status", "Status", 120),
                   ("data_hora", "Data/Hora", 150)]
        self.tree = ttk.Treeview(frame, columns=[c[0] for c in colunas],
                                 show="headings", selectmode="browse")
        for chave, titulo, largura in colunas:
            ancora = "center" if chave in ("id", "quantidade") else "w"
            self.tree.heading(chave, text=titulo)
            self.tree.column(chave, width=largura, anchor=ancora)

        barra = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=barra.set)
        self.tree.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.tree.tag_configure(PENDENTE, background="#fff4d6")
        self.tree.tag_configure(EM_ATENDIMENTO, background="#dcebff")
        self.tree.tag_configure(ATENDIDA, background="#dcf5dc")

    def _montar_acoes(self):
        box = ttk.Frame(self)
        box.pack(fill="x", pady=(10, 0))
        ttk.Button(box, text="Iniciar atendimento",
                   command=self.iniciar_atendimento).pack(side="left")
        ttk.Button(box, text="Concluir atendimento",
                   command=self.concluir).pack(side="left", padx=8)
        ttk.Button(box, text="Exportar CSV…",
                   command=self.exportar_csv).pack(side="right")

    def cadastrar(self):
        try:
            sol = self.service.criar(self.var_setor.get(), self.var_material.get(),
                                     self.var_quantidade.get(),
                                     self.var_prioridade.get())
        except SupriDeskError as e:
            messagebox.showwarning("Dados inválidos", str(e))
            return
        self.var_setor.set("")
        self.var_material.set("")
        self.var_quantidade.set("")
        self.var_prioridade.set(PRIORIDADES[0])
        self.ent_setor.focus_set()
        self.atualizar_tabela()
        self.var_info.set(f"Solicitação #{sol.id} cadastrada com status {sol.status}.")

    def _id_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecione uma solicitação",
                                "Clique em uma linha da tabela primeiro.")
            return None
        return int(sel[0])

    def _executar_transicao(self, funcao):
        id_ = self._id_selecionado()
        if id_ is None:
            return
        try:
            sol = funcao(id_)
        except SupriDeskError as e:
            messagebox.showwarning("Ação não permitida", str(e))
            return
        self.atualizar_tabela()
        if self.tree.exists(str(id_)):
            self.tree.selection_set(str(id_))
        self.var_info.set(f"Solicitação #{sol.id} agora está: {sol.status}.")

    def iniciar_atendimento(self):
        self._executar_transicao(self.service.iniciar_atendimento)

    def concluir(self):
        self._executar_transicao(self.service.concluir)

    def limpar_filtros(self):
        self.var_busca.set("")
        self.var_filtro.set(TODOS)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        filtro = self.var_filtro.get()
        status = "" if filtro == TODOS else filtro
        solicitacoes = self.service.listar(self.var_busca.get(), status)
        self.tree.delete(*self.tree.get_children())
        for s in solicitacoes:
            self.tree.insert("", "end", iid=str(s.id), tags=(s.status,), values=(
                s.id, s.setor, s.material, s.quantidade, s.prioridade,
                s.status, s.data_hora_br))
        self.var_info.set(f"{len(solicitacoes)} solicitação(ões) exibida(s).")

    def exportar_csv(self):
        sugestao = f"historico_supridesk_{datetime.now():%Y%m%d_%H%M%S}.csv"
        caminho = filedialog.asksaveasfilename(
            title="Exportar histórico", defaultextension=".csv",
            initialfile=sugestao, filetypes=[("Arquivo CSV", "*.csv")])
        if not caminho:
            return
        try:
            total = self.service.exportar_csv(caminho)
        except OSError as e:
            messagebox.showerror("Erro ao exportar", f"Não foi possível salvar:\n{e}")
            return
        messagebox.showinfo("Exportação concluída",
                            f"{total} registro(s) exportado(s) para:\n{caminho}")
