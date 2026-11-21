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
