# Projeto Previne

## Sobre o Projeto

O Projeto Previne é uma aplicação web desenvolvida em Python com Streamlit voltada para a prevenção do superendividamento e promoção da educação financeira.

A plataforma permite que usuários registrem suas receitas, despesas e dívidas, acompanhem sua situação financeira por meio de indicadores e relatórios, recebam alertas preventivos e tenham acesso a conteúdos educativos que auxiliam na tomada de decisões financeiras mais conscientes.

O sistema foi desenvolvido com foco em acessibilidade, organização financeira pessoal e análise de risco financeiro, oferecendo uma visão consolidada da saúde financeira do usuário.

---

## Funcionalidades

### Autenticação de Usuários

* Cadastro e login de usuários.
* Controle de sessões.
* Validação de acesso.

### Gestão Financeira

* Registro de receitas.
* Registro de despesas.
* Controle de lançamentos financeiros.
* Monitoramento do saldo financeiro.

### Controle de Dívidas

* Cadastro de dívidas.
* Acompanhamento de valores devidos.
* Visualização consolidada das obrigações financeiras.

### Dashboard Financeiro

* Visão geral da situação financeira.
* Indicadores e métricas financeiras.
* Resumo das movimentações registradas.

### Análise Inteligente de Risco

* Avaliação automática da situação financeira.
* Identificação de possíveis sinais de superendividamento.
* Classificação do nível de risco financeiro.

### Sistema de Alertas

* Geração de alertas preventivos.
* Notificações baseadas na análise financeira do usuário.
* Recomendações para melhoria da saúde financeira.

### Conteúdo Educacional

* Dicas de educação financeira.
* Orientações para planejamento financeiro.
* Conteúdo dinâmico armazenado em arquivo JSON.

### Relatórios

* Geração de relatórios financeiros.
* Consolidação das informações registradas.
* Apoio à análise da evolução financeira do usuário.

### Histórico Financeiro

* Registro das movimentações realizadas.
* Consulta de informações anteriores.

---

## Tecnologias Utilizadas

### Linguagem

* Python

### Interface

* Streamlit

### Banco de Dados

* SQLite

### Bibliotecas Principais

* Streamlit
* Pandas
* NumPy
* SQLite3

### Testes

* Pytest

---

## Estrutura do Projeto

```text
Projeto_Previne/
│
├── assets/
│   └── conteudos.json
│
├── data/
│   └── database.db
│
├── models/
│   ├── __init__.py
│   └── schemas.py
│
├── modules/
│   ├── alertas.py
│   ├── auth.py
│   ├── conteudo.py
│   ├── financeiro.py
│   ├── historico.py
│   ├── ia_engine.py
│   ├── relatorio.py
│   └── validacoes.py
│
├── pages/
│   ├── dashboard.py
│   ├── dividas.py
│   ├── lancamentos.py
│   └── relatorio.py
│
├── tests/
│   ├── __init__.py
│   └── test_backend.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Organização dos Módulos

| Módulo        | Responsabilidade                         |
| ------------- | ---------------------------------------- |
| auth.py       | Autenticação e gerenciamento de usuários |
| financeiro.py | Controle de receitas, despesas e saldo   |
| dividas.py    | Gerenciamento de dívidas                 |
| historico.py  | Histórico de movimentações               |
| alertas.py    | Geração de alertas financeiros           |
| ia_engine.py  | Análise de risco financeiro              |
| conteudo.py   | Carregamento de conteúdos educativos     |
| relatorio.py  | Emissão de relatórios                    |
| validacoes.py | Regras de validação dos dados            |
| schemas.py    | Estruturas e modelos de dados            |

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Mnascmento/Projeto_Previne.git
cd Projeto_Previne
```

### 2. Criar ambiente virtual

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/MacOS

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Executando a Aplicação

Inicie o sistema com:

```bash
streamlit run app.py
```

Após a execução, a aplicação ficará disponível no navegador através do endereço fornecido pelo Streamlit.

---

## Executando os Testes

Para executar os testes automatizados:

```bash
pytest
```

Ou:

```bash
pytest tests/
```

---

## Objetivo do Projeto

O Projeto Previne foi desenvolvido como uma solução tecnológica voltada para a prevenção do superendividamento, utilizando conceitos de desenvolvimento de software, persistência de dados, análise financeira e educação financeira digital.

A aplicação busca auxiliar usuários na compreensão de sua situação financeira e no desenvolvimento de hábitos que contribuam para uma gestão financeira mais saudável e sustentável.

---

## Autoras

**Mayara Almeida & Maria da Penha**

Estudantes de Análise e Desenvolvimento de Sistemas.
