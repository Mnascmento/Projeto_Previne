"""
modules/validacoes.py

Camada de validação de negócio — completamente desacoplada do banco de dados
e da UI do Streamlit. Isso permite:

  1. Testar todas as regras com pytest sem subir o app
  2. Reusar as mesmas validações em formulários diferentes
  3. Retornar múltiplos erros de uma só vez (não apenas o primeiro)

Decisão de arquitetura (T-07 da Sprint 2):
  Este módulo não importa nada de `modules.financeiro`, `models.schemas`
  ou `streamlit`. Só usa tipos primitivos e dataclasses da stdlib.

Uso:
    from modules.validacoes import validar_lancamento_gasto, validar_divida

    erros = validar_lancamento_gasto({"descricao": "", "valor": -10, ...})
    if erros:
        for e in erros:
            st.error(e)
"""

from __future__ import annotations
from datetime import date, datetime


# ── Constantes de domínio ──────────────────────────────────────────────────

CATEGORIAS_VALIDAS = {
    "Alimentação", "Moradia", "Transporte", "Saúde",
    "Educação", "Lazer", "Vestuário", "Outros",
}

TIPOS_RENDA_VALIDOS = {"fixa", "variavel"}

JUROS_MAXIMOS_SUSPEITOS = 30.0   # % a.m. — acima disso: aviso, não bloqueio

MAX_VALOR_UNICO = 1_000_000.0    # R$ 1 milhão: teto razoável para protótipo
MIN_DESC_CHARS   = 2
MAX_DESC_CHARS   = 120


# ── Validadores ────────────────────────────────────────────────────────────

def validar_renda(dados: dict) -> list[str]:
    """
    Valida um lançamento de renda.
    Recebe dict com chaves: descricao, valor, tipo, mes.
    Retorna lista de mensagens de erro (vazia = sem erros).
    """
    erros: list[str] = []

    desc  = (dados.get("descricao") or "").strip()
    valor = dados.get("valor")
    tipo  = dados.get("tipo")
    mes   = dados.get("mes")

    # Descrição
    if not desc:
        erros.append("Informe uma descrição para a renda.")
    elif len(desc) < MIN_DESC_CHARS:
        erros.append(f"Descrição deve ter pelo menos {MIN_DESC_CHARS} caracteres.")
    elif len(desc) > MAX_DESC_CHARS:
        erros.append(f"Descrição muito longa (máximo {MAX_DESC_CHARS} caracteres).")

    # Valor
    if valor is None:
        erros.append("Valor da renda é obrigatório.")
    elif not isinstance(valor, (int, float)):
        erros.append("Valor da renda deve ser um número.")
    elif valor <= 0:
        erros.append("Valor da renda deve ser maior que zero.")
    elif valor > MAX_VALOR_UNICO:
        erros.append(f"Valor muito alto. Máximo aceito: R$ {MAX_VALOR_UNICO:,.2f}.")

    # Tipo
    if tipo not in TIPOS_RENDA_VALIDOS:
        erros.append(f"Tipo de renda inválido. Use: {', '.join(TIPOS_RENDA_VALIDOS)}.")

    # Mês
    if not mes:
        erros.append("Mês de referência é obrigatório.")
    else:
        try:
            datetime.strptime(mes, "%Y-%m")
        except ValueError:
            erros.append("Mês inválido. Formato esperado: YYYY-MM.")

    return erros


def validar_lancamento_gasto(dados: dict) -> list[str]:
    """
    Valida um lançamento de gasto.
    Recebe dict com chaves: descricao, categoria, valor, data.
    Retorna lista de mensagens de erro.
    """
    erros: list[str] = []

    desc      = (dados.get("descricao") or "").strip()
    categoria = dados.get("categoria")
    valor     = dados.get("valor")
    data_g    = dados.get("data")

    # Descrição
    if not desc:
        erros.append("Informe uma descrição para o gasto.")
    elif len(desc) < MIN_DESC_CHARS:
        erros.append(f"Descrição deve ter pelo menos {MIN_DESC_CHARS} caracteres.")
    elif len(desc) > MAX_DESC_CHARS:
        erros.append(f"Descrição muito longa (máximo {MAX_DESC_CHARS} caracteres).")

    # Categoria
    if not categoria:
        erros.append("Selecione uma categoria.")
    elif categoria not in CATEGORIAS_VALIDAS:
        erros.append(f"Categoria inválida: '{categoria}'.")

    # Valor
    if valor is None:
        erros.append("Valor do gasto é obrigatório.")
    elif not isinstance(valor, (int, float)):
        erros.append("Valor do gasto deve ser um número.")
    elif valor <= 0:
        erros.append("Valor do gasto deve ser maior que zero.")
    elif valor > MAX_VALOR_UNICO:
        erros.append(f"Valor muito alto. Máximo aceito: R$ {MAX_VALOR_UNICO:,.2f}.")

    # Data
    if data_g is None:
        erros.append("Data do gasto é obrigatória.")
    elif isinstance(data_g, str):
        try:
            datetime.strptime(data_g, "%Y-%m-%d")
        except ValueError:
            erros.append("Data inválida. Formato esperado: YYYY-MM-DD.")
    elif not isinstance(data_g, date):
        erros.append("Data do gasto inválida.")

    return erros


def validar_divida(dados: dict) -> list[str]:
    """
    Valida o cadastro de uma dívida.
    Recebe dict com: descricao, valor_total, valor_parcela,
                     parcelas_restantes, taxa_juros, vencimento.
    Retorna lista de mensagens de erro. Avisos (não bloqueantes)
    são retornados com prefixo '⚠ '.
    """
    erros: list[str] = []

    desc           = (dados.get("descricao") or "").strip()
    valor_total    = dados.get("valor_total")
    valor_parcela  = dados.get("valor_parcela")
    parc_rest      = dados.get("parcelas_restantes")
    taxa           = dados.get("taxa_juros", 0.0)
    vencimento     = dados.get("vencimento")

    # Descrição
    if not desc:
        erros.append("Informe uma descrição para a dívida.")
    elif len(desc) < MIN_DESC_CHARS:
        erros.append(f"Descrição deve ter pelo menos {MIN_DESC_CHARS} caracteres.")
    elif len(desc) > MAX_DESC_CHARS:
        erros.append(f"Descrição muito longa (máximo {MAX_DESC_CHARS} caracteres).")

    # Valor total
    if valor_total is None:
        erros.append("Valor total da dívida é obrigatório.")
    elif not isinstance(valor_total, (int, float)):
        erros.append("Valor total deve ser um número.")
    elif valor_total <= 0:
        erros.append("Valor total deve ser maior que zero.")

    # Valor parcela
    if valor_parcela is None:
        erros.append("Valor da parcela é obrigatório.")
    elif not isinstance(valor_parcela, (int, float)):
        erros.append("Valor da parcela deve ser um número.")
    elif valor_parcela <= 0:
        erros.append("Valor da parcela deve ser maior que zero.")

    # Consistência parcela x total
    if (
        isinstance(valor_parcela, (int, float)) and valor_parcela > 0
        and isinstance(valor_total, (int, float)) and valor_total > 0
        and valor_parcela > valor_total
    ):
        erros.append("Parcela não pode ser maior que o valor total da dívida.")

    # Parcelas restantes
    if parc_rest is None:
        erros.append("Informe o número de parcelas restantes.")
    elif not isinstance(parc_rest, int):
        try:
            parc_rest = int(parc_rest)
        except (TypeError, ValueError):
            erros.append("Parcelas restantes deve ser um número inteiro.")
            parc_rest = None
    if isinstance(parc_rest, int) and parc_rest < 1:
        erros.append("Parcelas restantes deve ser pelo menos 1.")

    # Taxa de juros — aviso, não bloqueio
    if isinstance(taxa, (int, float)) and taxa > JUROS_MAXIMOS_SUSPEITOS:
        erros.append(
            f"⚠ Taxa de juros de {taxa:.1f}% a.m. parece muito alta. "
            f"Confirme antes de salvar."
        )

    # Vencimento
    if vencimento is not None:
        try:
            venc_int = int(vencimento)
            if not (1 <= venc_int <= 31):
                erros.append("Dia de vencimento deve ser entre 1 e 31.")
        except (TypeError, ValueError):
            erros.append("Dia de vencimento inválido.")

    return erros


def validar_usuario_cadastro(dados: dict) -> list[str]:
    """
    Valida os dados de cadastro de novo usuário.
    Recebe dict com: username, email, senha, senha_confirmacao.
    """
    erros: list[str] = []

    username  = (dados.get("username") or "").strip()
    email     = (dados.get("email") or "").strip().lower()
    senha     = dados.get("senha") or ""
    senha2    = dados.get("senha_confirmacao") or ""

    # Username
    if not username:
        erros.append("Nome de usuário é obrigatório.")
    elif len(username) < 3:
        erros.append("Nome de usuário deve ter pelo menos 3 caracteres.")
    elif len(username) > 80:
        erros.append("Nome de usuário muito longo (máximo 80 caracteres).")

    # E-mail
    if not email:
        erros.append("E-mail é obrigatório.")
    elif "@" not in email or "." not in email.split("@")[-1]:
        erros.append("E-mail inválido.")
    elif len(email) > 120:
        erros.append("E-mail muito longo.")

    # Senha
    if not senha:
        erros.append("Senha é obrigatória.")
    elif len(senha) < 6:
        erros.append("Senha deve ter pelo menos 6 caracteres.")
    elif len(senha) > 128:
        erros.append("Senha muito longa.")

    # Confirmação
    if senha and senha2 and senha != senha2:
        erros.append("As senhas não coincidem.")
    elif senha and not senha2:
        erros.append("Confirme a senha.")

    return erros


# ── Utilitários ────────────────────────────────────────────────────────────

def separar_erros_e_avisos(mensagens: list[str]) -> tuple[list[str], list[str]]:
    """
    Separa a lista de mensagens em erros bloqueantes e avisos (prefixo '⚠ ').
    Retorna (erros, avisos).
    """
    erros  = [m for m in mensagens if not m.startswith("⚠")]
    avisos = [m for m in mensagens if m.startswith("⚠")]
    return erros, avisos
