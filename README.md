# Cadastro de Alunos

Sistema CRUD com interface gráfica desenvolvido em Python para a disciplina
INE5201 - Introdução à Ciência da Computação, da Universidade Federal de
Santa Catarina.

## Funcionalidades

- cadastro de alunos com matrícula, nome, curso e email;
- tabela com todos os registros cadastrados;
- busca por nome ou matrícula;
- edição e exclusão de registros;
- confirmação antes da exclusão;
- validação de campos obrigatórios, matrícula e email;
- impedimento de matrículas repetidas;
- persistência dos dados em SQLite;
- exportação opcional da lista pesquisada para CSV.

## Esquema do banco de dados

O arquivo `alunos.db` contém a tabela `alunos`, criada pelo script
`banco.sql`:

| Campo | Tipo | Regra |
| --- | --- | --- |
| `matricula` | TEXT | Chave primária |
| `nome` | TEXT | Não nulo |
| `curso` | TEXT | Não nulo |
| `email` | TEXT | Opcional |
| `data_cadastro` | TIMESTAMP | Data padrão atual |

## Requisitos

- Python 3.8 ou superior;
- `tkinter`, normalmente incluído na instalação padrão do Python.

Não há dependências externas.

## Como executar

Na pasta do projeto, execute:

```bash
python cadastro_alunos.py
```

Na primeira execução, o banco `alunos.db` e a tabela `alunos` são criados
automaticamente. Os dados permanecem após fechar o programa.

## Testes

Execute os testes automatizados com:

```bash
python -m unittest test_cadastro_alunos.py
```

Os testes cobrem cadastro, busca, matrícula repetida, atualização, exclusão,
busca por nome ou matrícula e validações.

## Estrutura do projeto

| Arquivo | Descrição |
| --- | --- |
| `cadastro_alunos.py` | Interface gráfica e operações CRUD. |
| `banco.sql` | Script de criação da tabela. |
| `test_cadastro_alunos.py` | Testes das regras e do banco. |
| `alunos.db` | Banco SQLite criado ao executar o programa. |
| `screenshot_sistema.png` | Captura do sistema em execução. |

## Uso do GitHub Copilot

O GitHub Copilot foi utilizado como assistente para organizar o esquema
SQLite, separar as operações CRUD, preparar a interface `tkinter`, criar testes
e documentar o projeto. Todas as sugestões foram revisadas e adaptadas antes
da execução e validação.
