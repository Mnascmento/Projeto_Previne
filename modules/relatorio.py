"""
modules/relatorio.py

Geração de relatório mensal do usuário.

Para o protótipo acadêmico: gera texto formatado para download (.txt).
A estrutura está preparada para substituição por PDF (ReportLab/WeasyPrint)
sem alterar a interface das funções.
"""

from __future__ import annotations
from datetime import datetime
from modules.ia_engine import ResultadoRisco, NIVEL_LABEL


def gerar_relatorio_texto(
    username: str,
    mes: str,
    renda_total: float,
    total_gastos: float,
    total_parcelas: float,
    gastos_por_cat: dict[str, float],
    dividas: list[dict],
    resultado: ResultadoRisco,
) -> str:
    """
    Gera o relatório completo em texto formatado ASCII.
    Retorna a string pronta para download via st.download_button.
    """
    sep  = "=" * 56
    sep2 = "─" * 56
    now  = datetime.now().strftime("%d/%m/%Y às %H:%M")

    linhas = [
        sep,
        "  💡 PREVINE — RELATÓRIO FINANCEIRO MENSAL",
        sep,
        f"  Usuário  : {username}",
        f"  Período  : {_formatar_mes(mes)}",
        f"  Gerado   : {now}",
        sep,
        "",
        sep2,
        "  RESUMO FINANCEIRO",
        sep2,
        f"  Renda total            : R$ {renda_total:>10,.2f}",
        f"  Total de gastos        : R$ {total_gastos:>10,.2f}",
        f"  Parcelas de dívidas    : R$ {total_parcelas:>10,.2f}",
        f"  ─────────────────────────────────────────",
        f"  Saldo livre            : R$ {resultado.saldo_livre:>10,.2f}",
        f"  Comprometimento        : {resultado.comprometimento:>9.1f}%",
        "",
        sep2,
        "  ÍNDICE DE RISCO (IA PREDITIVA)",
        sep2,
        f"  Pontuação  : {resultado.indice:.0f} / 100",
        f"  Nível      : {NIVEL_LABEL.get(resultado.nivel, resultado.nivel)}",
        "",
    ]

    # Motivos do risco
    if resultado.motivos:
        linhas.append("  Fatores identificados:")
        for m in resultado.motivos:
            linhas.append(f"    ⚠  {m}")
        linhas.append("")

    # Detalhes por feature
    if resultado.detalhes:
        linhas += [
            sep2,
            "  DETALHAMENTO DO SCORE POR VARIÁVEL",
            sep2,
            f"  {'Variável':<22} {'Valor':<12} {'Contribuição':>12}",
            f"  {'─'*22} {'─'*12} {'─'*12}",
        ]
        for d in resultado.detalhes:
            linhas.append(
                f"  {d.nome:<22} {_formatar_valor_feature(d.nome, d.valor_bruto):<12} "
                f"  {d.contribuicao:>8.1f} pts"
            )
        linhas.append("")

    # Gastos por categoria
    linhas += [
        sep2,
        "  GASTOS POR CATEGORIA",
        sep2,
    ]
    if gastos_por_cat:
        total_g = sum(gastos_por_cat.values()) or 1
        for cat, val in sorted(gastos_por_cat.items(), key=lambda x: -x[1]):
            pct = val / total_g * 100
            barra = "█" * int(pct / 5)
            linhas.append(f"  {cat:<20} R$ {val:>8,.2f}  {pct:>4.0f}%  {barra}")
    else:
        linhas.append("  Nenhum gasto registrado neste mês.")
    linhas.append("")

    # Dívidas ativas
    linhas += [
        sep2,
        "  DÍVIDAS ATIVAS",
        sep2,
    ]
    if dividas:
        for d in dividas:
            taxa_str = f"{d['taxa_juros']:.1f}% a.m." if d.get("taxa_juros") else "s/ juros"
            venc_str = f"dia {d['vencimento']}" if d.get("vencimento") else "─"
            linhas.append(
                f"  {d['descricao'][:28]:<28} "
                f"R$ {d['valor_parcela']:>7,.2f}/mês × {d['parcelas_restantes']:>3}× "
                f"| {taxa_str:<12} | vence {venc_str}"
            )
    else:
        linhas.append("  Nenhuma dívida ativa. 🎉")
    linhas.append("")

    linhas += [
        sep,
        "  Relatório gerado pelo Previne · Faculdade Senac Pernambuco",
        "  Jennifer Mayara & Maria da Penha — Projeto Acadêmico 2026",
        sep,
    ]

    return "\n".join(linhas)


# ── Helpers ────────────────────────────────────────────────────────────────

def _formatar_mes(mes: str) -> str:
    """YYYY-MM → 'Junho de 2026'"""
    meses_pt = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]
    try:
        ano, m = mes.split("-")
        return f"{meses_pt[int(m)]} de {ano}"
    except Exception:
        return mes


def _formatar_valor_feature(nome: str, valor: float) -> str:
    """Formata o valor bruto de uma feature de forma legível."""
    if nome == "comprometimento":
        return f"{valor:.1f}%"
    if nome in ("num_dividas", "atrasos", "historico"):
        return f"{int(valor)}"
    if nome == "maior_juros":
        return f"{valor:.1f}% a.m."
    return f"{valor:.2f}"
