import csv
import re
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


ARQUIVO_BANCO = Path(__file__).with_name("alunos.db")
ARQUIVO_SQL = Path(__file__).with_name("banco.sql")


def criar_conexao(arquivo=ARQUIVO_BANCO):
    conexao = sqlite3.connect(str(arquivo))
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela(conexao):
    sql = ARQUIVO_SQL.read_text(encoding="utf-8")
    conexao.executescript(sql)
    conexao.commit()


def validar_matricula(matricula):
    return bool(re.fullmatch(r"[A-Za-z0-9-]+", matricula.strip()))


def validar_email(email):
    if not email:
        return True
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))


def inserir_aluno(dados, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabela(conexao)
        conexao.execute(
            """
            INSERT INTO alunos (matricula, nome, curso, email)
            VALUES (?, ?, ?, ?)
            """,
            (
                dados["matricula"].strip(),
                dados["nome"].strip(),
                dados["curso"].strip(),
                dados["email"].strip() or None,
            ),
        )
        conexao.commit()
        return True, "Aluno cadastrado com sucesso."
    except sqlite3.IntegrityError:
        return False, "Já existe um aluno com essa matrícula."
    except sqlite3.Error as erro:
        return False, f"Erro ao cadastrar aluno: {erro}"
    finally:
        if fechar:
            conexao.close()


def buscar_aluno(matricula, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabela(conexao)
        linha = conexao.execute(
            "SELECT * FROM alunos WHERE matricula = ?",
            (matricula.strip(),),
        ).fetchone()
        return dict(linha) if linha else None
    finally:
        if fechar:
            conexao.close()


def atualizar_aluno(dados, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabela(conexao)
        cursor = conexao.execute(
            """
            UPDATE alunos
            SET nome = ?, curso = ?, email = ?
            WHERE matricula = ?
            """,
            (
                dados["nome"].strip(),
                dados["curso"].strip(),
                dados["email"].strip() or None,
                dados["matricula"].strip(),
            ),
        )
        conexao.commit()
        if cursor.rowcount:
            return True, "Aluno atualizado com sucesso."
        return False, "Aluno não encontrado."
    except sqlite3.Error as erro:
        return False, f"Erro ao atualizar aluno: {erro}"
    finally:
        if fechar:
            conexao.close()


def excluir_aluno(matricula, conexao=None):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabela(conexao)
        cursor = conexao.execute(
            "DELETE FROM alunos WHERE matricula = ?",
            (matricula.strip(),),
        )
        conexao.commit()
        if cursor.rowcount:
            return True, "Aluno excluído com sucesso."
        return False, "Aluno não encontrado."
    except sqlite3.Error as erro:
        return False, f"Erro ao excluir aluno: {erro}"
    finally:
        if fechar:
            conexao.close()


def listar_todos(conexao=None, termo=""):
    fechar = conexao is None
    conexao = conexao or criar_conexao()
    try:
        criar_tabela(conexao)
        termo = termo.strip()
        if termo:
            consulta = """
                SELECT * FROM alunos
                WHERE LOWER(nome) LIKE ? OR LOWER(matricula) LIKE ?
                ORDER BY nome
            """
            filtro = f"%{termo.lower()}%"
            linhas = conexao.execute(consulta, (filtro, filtro)).fetchall()
        else:
            linhas = conexao.execute(
                "SELECT * FROM alunos ORDER BY nome"
            ).fetchall()
        return [dict(linha) for linha in linhas]
    finally:
        if fechar:
            conexao.close()


class CadastroAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Alunos")
        self.root.geometry("920x560")
        self.root.minsize(820, 520)
        self.conexao = criar_conexao()
        criar_tabela(self.conexao)

        self.matricula = tk.StringVar()
        self.nome = tk.StringVar()
        self.curso = tk.StringVar()
        self.email = tk.StringVar()
        self.busca = tk.StringVar()
        self.status = tk.StringVar(value="Sistema pronto.")

        self.criar_layout()
        self.atualizar_tabela()

    def criar_layout(self):
        titulo = tk.Label(
            self.root,
            text="CADASTRO DE ALUNOS",
            font=("Arial", 20, "bold"),
            fg="#17324D",
            pady=10,
        )
        titulo.pack(fill=tk.X)

        formulario = tk.LabelFrame(
            self.root,
            text="Dados do aluno",
            padx=12,
            pady=8,
        )
        formulario.pack(fill=tk.X, padx=12, pady=(0, 8))

        campos = (
            ("Matrícula:", self.matricula),
            ("Nome:", self.nome),
            ("Curso:", self.curso),
            ("Email:", self.email),
        )
        for linha, (rotulo, variavel) in enumerate(campos):
            tk.Label(formulario, text=rotulo, width=10, anchor="w").grid(
                row=linha,
                column=0,
                padx=4,
                pady=4,
                sticky="w",
            )
            tk.Entry(formulario, textvariable=variavel, width=38).grid(
                row=linha,
                column=1,
                padx=4,
                pady=4,
                sticky="w",
            )

        acoes = tk.Frame(formulario)
        acoes.grid(row=0, column=2, rowspan=4, padx=(24, 4), pady=4)
        tk.Button(acoes, text="Cadastrar", command=self.cadastrar, width=12).grid(
            row=0, column=0, padx=3, pady=3
        )
        tk.Button(acoes, text="Editar", command=self.editar, width=12).grid(
            row=1, column=0, padx=3, pady=3
        )
        tk.Button(acoes, text="Excluir", command=self.excluir, width=12).grid(
            row=2, column=0, padx=3, pady=3
        )
        tk.Button(acoes, text="Limpar", command=self.limpar, width=12).grid(
            row=3, column=0, padx=3, pady=3
        )

        pesquisa = tk.Frame(self.root)
        pesquisa.pack(fill=tk.X, padx=12)
        tk.Label(pesquisa, text="Buscar por nome ou matrícula:").pack(side=tk.LEFT)
        tk.Entry(pesquisa, textvariable=self.busca, width=36).pack(
            side=tk.LEFT, padx=8
        )
        tk.Button(pesquisa, text="Buscar", command=self.buscar, width=10).pack(
            side=tk.LEFT
        )
        tk.Button(
            pesquisa,
            text="Exportar CSV",
            command=self.exportar_csv,
            width=12,
        ).pack(side=tk.RIGHT)

        tabela_frame = tk.Frame(self.root)
        tabela_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        colunas = ("matricula", "nome", "curso", "email", "data_cadastro")
        self.tabela = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )
        cabecalhos = (
            ("matricula", "Matrícula", 100),
            ("nome", "Nome", 190),
            ("curso", "Curso", 170),
            ("email", "Email", 220),
            ("data_cadastro", "Cadastro", 140),
        )
        for coluna, texto, largura in cabecalhos:
            self.tabela.heading(coluna, text=texto)
            self.tabela.column(coluna, width=largura, anchor="w")

        barra_vertical = ttk.Scrollbar(
            tabela_frame,
            orient=tk.VERTICAL,
            command=self.tabela.yview,
        )
        barra_horizontal = ttk.Scrollbar(
            tabela_frame,
            orient=tk.HORIZONTAL,
            command=self.tabela.xview,
        )
        self.tabela.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        self.tabela.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")
        tabela_frame.rowconfigure(0, weight=1)
        tabela_frame.columnconfigure(0, weight=1)
        self.tabela.bind("<<TreeviewSelect>>", self.selecionar)

        tk.Label(
            self.root,
            textvariable=self.status,
            anchor="w",
            relief=tk.SUNKEN,
            padx=8,
        ).pack(fill=tk.X, side=tk.BOTTOM)

    def dados_formulario(self):
        return {
            "matricula": self.matricula.get(),
            "nome": self.nome.get(),
            "curso": self.curso.get(),
            "email": self.email.get(),
        }

    def validar_formulario(self, dados):
        if not dados["matricula"].strip():
            return "Informe a matrícula."
        if not dados["nome"].strip():
            return "Informe o nome."
        if not dados["curso"].strip():
            return "Informe o curso."
        if not validar_matricula(dados["matricula"]):
            return "A matrícula deve conter apenas letras, números ou hífens."
        if not validar_email(dados["email"]):
            return "Formato de email inválido."
        return None

    def cadastrar(self):
        dados = self.dados_formulario()
        erro = self.validar_formulario(dados)
        if erro:
            messagebox.showwarning("Validação", erro)
            self.status.set(erro)
            return

        sucesso, mensagem = inserir_aluno(dados, self.conexao)
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Cadastro", mensagem)
            self.limpar()
        else:
            messagebox.showerror("Erro", mensagem)

    def editar(self):
        dados = self.dados_formulario()
        erro = self.validar_formulario(dados)
        if erro:
            messagebox.showwarning("Validação", erro)
            self.status.set(erro)
            return

        sucesso, mensagem = atualizar_aluno(dados, self.conexao)
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Edição", mensagem)
            self.atualizar_tabela()
            self.limpar()
        else:
            messagebox.showerror("Erro", mensagem)

    def excluir(self):
        matricula = self.matricula.get().strip()
        if not matricula:
            messagebox.showwarning("Validação", "Selecione um aluno para excluir.")
            return
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir o aluno de matrícula {matricula}?",
        ):
            return

        sucesso, mensagem = excluir_aluno(matricula, self.conexao)
        self.status.set(mensagem)
        if sucesso:
            messagebox.showinfo("Exclusão", mensagem)
            self.atualizar_tabela()
            self.limpar()
        else:
            messagebox.showerror("Erro", mensagem)

    def buscar(self):
        self.atualizar_tabela(self.busca.get())

    def atualizar_tabela(self, termo=""):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        alunos = listar_todos(self.conexao, termo)
        for aluno in alunos:
            self.tabela.insert(
                "",
                tk.END,
                values=(
                    aluno["matricula"],
                    aluno["nome"],
                    aluno["curso"],
                    aluno["email"] or "",
                    aluno["data_cadastro"],
                ),
            )
        self.status.set(f"{len(alunos)} aluno(s) encontrado(s).")

    def selecionar(self, event=None):
        selecionado = self.tabela.selection()
        if not selecionado:
            return
        valores = self.tabela.item(selecionado[0], "values")
        self.matricula.set(valores[0])
        self.nome.set(valores[1])
        self.curso.set(valores[2])
        self.email.set(valores[3])
        self.status.set(f"Aluno {valores[0]} selecionado.")

    def limpar(self):
        self.matricula.set("")
        self.nome.set("")
        self.curso.set("")
        self.email.set("")
        self.busca.set("")
        self.status.set("Formulário limpo.")
        self.atualizar_tabela()

    def exportar_csv(self):
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
            initialfile="alunos.csv",
        )
        if not caminho:
            return
        alunos = listar_todos(self.conexao, self.busca.get())
        try:
            with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(
                    ("Matrícula", "Nome", "Curso", "Email", "Data de cadastro")
                )
                for aluno in alunos:
                    escritor.writerow(
                        (
                            aluno["matricula"],
                            aluno["nome"],
                            aluno["curso"],
                            aluno["email"] or "",
                            aluno["data_cadastro"],
                        )
                    )
            messagebox.showinfo("Exportação", "Lista exportada com sucesso.")
        except OSError as erro:
            messagebox.showerror("Erro", f"Não foi possível exportar: {erro}")

    def fechar(self):
        self.conexao.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CadastroAlunos(root)
    root.protocol("WM_DELETE_WINDOW", app.fechar)
    root.mainloop()


if __name__ == "__main__":
    main()
