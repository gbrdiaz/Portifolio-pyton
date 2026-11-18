# SupriDesk — Sistema de gestão de solicitações de materiais

Sistema desktop para organizar pedidos internos de materiais (cabos, periféricos,
papel, itens de escritório), acompanhar o andamento do atendimento e consultar o
histórico. Trabalho individual de **Desenvolvimento Rápido de Aplicações em Python
(2026.2)**.

**Autor:** _(seu nome e matrícula aqui)_

## Requisitos

- **Python 3.9 ou superior** (testado com Python 3.12)
- **Tkinter** (já vem com o Python no Windows/macOS; no Linux Debian/Ubuntu:
  `sudo apt install python3-tk`)
- **Nenhuma dependência externa:** apenas biblioteca padrão (`tkinter`, `sqlite3`,
  `csv`, `datetime`, `unittest`). Por isso o `requirements.txt` não lista pacotes.

## Como executar

```bash
git clone <link-do-repositorio>
cd supridesk
python main.py
```

O arquivo `solicitacoes.db` é criado automaticamente na primeira execução, na pasta
em que o comando é executado.

## Funcionalidades

- **Cadastro** de Setor, Material, Quantidade e Prioridade (Normal/Alta). O ID e a
  data/hora são gerados automaticamente e o status inicial é **Pendente**.
- **Validações:** campos vazios são bloqueados; a quantidade deve ser um inteiro
  positivo (recusa `0`, negativos, decimais e texto).
- **Fluxo de atendimento:** `Pendente → Em atendimento → Atendida`, com um botão para
  cada ação (**Iniciar atendimento** e **Concluir atendimento**). Transições inválidas
  (pular etapa ou repetir) são bloqueadas com aviso.
- **Persistência** em SQLite, sempre com consultas parametrizadas (`?`).
- **Pesquisa** por Setor ou Material (por trecho, sem diferenciar maiúsculas de
  minúsculas), **filtro por Status** e botão **Limpar filtros**. A tabela é
  atualizada após cada operação.
- **Exportação CSV** (botão **Exportar CSV…**) do histórico completo com cabeçalho
  (`ID;Setor;Material;Quantidade;Prioridade;Status;Data/Hora`). Usa `;` como
  separador e UTF-8 com BOM para abrir corretamente no Excel em português. Valores de
  texto que começam com `=`, `+`, `-` ou `@` recebem um `'` na frente para evitar
  injeção de fórmulas na planilha.

## Estrutura do projeto

```
supridesk/
├── main.py                 # ponto de entrada
├── requirements.txt
├── README.md
├── .gitignore
├── supridesk/
│   ├── __init__.py
│   ├── database.py         # acesso ao SQLite (SQL parametrizado)
│   ├── services.py         # regras de negócio: validação, fluxo de status, CSV
│   └── ui.py               # interface Tkinter/ttk (sem SQL e sem regras)
└── tests/
    ├── __init__.py
    └── test_services.py    # testes automatizados das regras
```

Separação de responsabilidades: a **interface** só coleta dados e exibe mensagens; as
**regras de negócio** (`SolicitacaoService`) decidem o que é válido; o **banco**
(`Database`) apenas lê e grava.

## Testes

### Testes manuais (pela interface)

1. Cadastre **TI / Mouse USB / 5 / Alta** → a linha aparece com status **Pendente**.
2. Tente cadastrar **Administrativo / Papel A4 / 0 / Normal** → a operação é recusada
   com mensagem de erro e nada é gravado.
3. Faça **Pendente → Em atendimento → Atendida**: selecione o registro, clique em
   **Iniciar atendimento** e depois em **Concluir atendimento**. Tente **Concluir
   atendimento** de novo → é bloqueado com aviso.
4. Feche e reabra o sistema (`python main.py`) → o registro continua na tabela.
5. Pesquise **Mouse** ou **TI**, filtre por Status **Atendida** e clique em **Exportar
   CSV…**; abra o arquivo gerado e confira o cabeçalho e os dados.

### Testes automatizados

```bash
python -m unittest -v
```

Cobrem: cadastro com status Pendente, recusa de quantidade inválida e campos vazios,
fluxo e bloqueio de transições, persistência após reabrir o banco, busca e filtro,
tentativa de SQL injection e conteúdo do CSV.

## Uso de ferramentas de IA

_(Preencha com sinceridade antes de entregar: diga quais ferramentas usou, para que
partes do projeto, e o que você mesmo revisou/alterou. Informe também qualquer trecho
de código que veio de outra fonte, como site ou tutorial. Exemplo:)_ Utilizei o Claude
(Anthropic) para gerar a primeira versão do código a partir do enunciado e para revisar
o README. Depois li e testei cada módulo, e consigo explicar as decisões principais:
separação em três camadas, uso de `?` nas consultas, tabela de transições de status e
exportação CSV com `;` e BOM.
