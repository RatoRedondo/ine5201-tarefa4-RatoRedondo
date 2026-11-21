import tempfile
import unittest
from pathlib import Path

from cadastro_alunos import (
    atualizar_aluno,
    buscar_aluno,
    criar_conexao,
    criar_tabela,
    excluir_aluno,
    inserir_aluno,
    listar_todos,
    validar_email,
    validar_matricula,
)


class CadastroAlunosTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.arquivo = Path(self.temp.name) / "teste.db"
        self.conexao = criar_conexao(self.arquivo)
        criar_tabela(self.conexao)

    def tearDown(self):
        self.conexao.close()
        self.temp.cleanup()

    def aluno(self, matricula="2026001"):
        return {
            "matricula": matricula,
            "nome": "Ana Silva",
            "curso": "Ciência da Computação",
            "email": "ana@exemplo.com",
        }

    def test_insere_e_busca_aluno(self):
        sucesso, _ = inserir_aluno(self.aluno(), self.conexao)

        encontrado = buscar_aluno("2026001", self.conexao)
        self.assertTrue(sucesso)
        self.assertEqual(encontrado["nome"], "Ana Silva")

    def test_rejeita_matricula_repetida(self):
        inserir_aluno(self.aluno(), self.conexao)

        sucesso, mensagem = inserir_aluno(self.aluno(), self.conexao)

        self.assertFalse(sucesso)
        self.assertIn("matrícula", mensagem.lower())

    def test_atualiza_e_exclui_aluno(self):
        inserir_aluno(self.aluno(), self.conexao)
        dados = self.aluno()
        dados["nome"] = "Ana Souza"

        atualizar_aluno(dados, self.conexao)
        encontrado = buscar_aluno("2026001", self.conexao)
        sucesso, _ = excluir_aluno("2026001", self.conexao)

        self.assertEqual(encontrado["nome"], "Ana Souza")
        self.assertTrue(sucesso)
        self.assertIsNone(buscar_aluno("2026001", self.conexao))

    def test_busca_por_nome_e_matricula(self):
        inserir_aluno(self.aluno(), self.conexao)

        por_nome = listar_todos(self.conexao, "Ana")
        por_matricula = listar_todos(self.conexao, "2026")

        self.assertEqual(len(por_nome), 1)
        self.assertEqual(len(por_matricula), 1)

    def test_valida_matricula_e_email(self):
        self.assertTrue(validar_matricula("2026-A"))
        self.assertFalse(validar_matricula("2026 A"))
        self.assertTrue(validar_email("aluno@universidade.br"))
        self.assertFalse(validar_email("aluno-invalido"))


if __name__ == "__main__":
    unittest.main()
