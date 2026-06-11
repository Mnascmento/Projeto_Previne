# 💡 Previsão Inteligente

App de controle financeiro pessoal com IA preditiva de risco de superendividamento.  
Desenvolvido como protótipo acadêmico com Streamlit + SQLite.

---

## Estrutura

```
previsao_inteligente/
├── app.py                  # Ponto de entrada
├── requirements.txt
├── data/database.db        # SQLite (criado automaticamente)
├── modules/
│   ├── auth.py             # Cadastro e sessão
│   ├── financeiro.py       # Renda, gastos, dívidas (CRUD)
│   ├── ia_engine.py        # Cálculo do índice de risco por regras pontuadas
│   ├── alertas.py          # Geração de alertas e sugestões corretivas
│   ├── conteudo.py         # Dicas educativas contextualizadas
│   └── relatorio.py        # Geração de relatório em texto
├── pages/
│   ├── dashboard.py        # Painel principal com gauge de risco
│   ├── lancamentos.py      # Entrada de rendas e gastos
│   ├── dividas.py          # Gestão de dívidas e parcelas
│   └── relatorio.py        # Visualização e download do relatório
└── assets/conteudos.json   # Base de dicas educativas
```

---

## Como rodar

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o app
streamlit run app.py
```

O banco de dados `data/database.db` é criado automaticamente na primeira execução.

---

## Motor de IA (regras pontuadas)

O índice de risco (0–100) é calculado por 4 fatores:

| Fator | Pontos |
|---|---|
| Comprometimento ≥ 30% da renda | +10 |
| Comprometimento ≥ 50% da renda | +20 |
| Comprometimento ≥ 70% da renda | +30 |
| Comprometimento ≥ 90% da renda | +40 |
| Parcelas > 20% da renda | +15 |
| Parcelas > 40% da renda | +30 |
| 3+ dívidas ativas | +10 |
| 5+ dívidas ativas | +20 |
| Saldo mensal negativo | +20 |

**Classificação:** 0–29 Baixo · 30–54 Médio · 55–79 Alto · 80–100 Crítico

---

## Fora do escopo (protótipo)

- Autenticação robusta / criptografia
- Open Finance / notificações push
- Deploy em nuvem
- Testes automatizados
