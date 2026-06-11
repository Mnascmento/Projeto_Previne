"""
modules/alertas.py

Gera alertas e sugestões corretivas com base no ResultadoRisco do ia_engine.

Lógica de negócio separada da UI — as funções retornam estruturas de dados
simples que as páginas renderizam da forma que quiserem.

Alertas: situações detectadas (descritivo)
Sugestões: ações concretas que o usuário deve tomar (prescritivo)
"""

from __future__ import annotations
from modules.ia_engine import ResultadoRisco


# ── Tipos de alerta ────────────────────────────────────────────────────────
# tipo: 'info' | 'aviso' | 'perigo'
# Mapeiam para verde / amarelo / vermelho na UI.

def gerar_alertas(resultado: ResultadoRisco, renda: float) -> list[dict]:
    """
    Retorna lista de alertas relevantes para o resultado atual.
    Formato: [{tipo, titulo, descricao}]
    """
    alertas: list[dict] = []
    nivel = resultado.nivel
    comp  = resultado.comprometimento
    saldo = resultado.saldo_livre

    # ── Saldo negativo ────────────────────────────────────────────────────
    if saldo < 0:
        alertas.append({
            "tipo": "perigo",
            "titulo": "⚠️ Saldo mensal negativo",
            "descricao": (
                f"Seus compromissos superam a renda em R$ {abs(saldo):,.2f}. "
                "Corte gastos não essenciais imediatamente."
            ),
        })

    # ── Comprometimento crítico ───────────────────────────────────────────
    elif comp >= 90:
        alertas.append({
            "tipo": "perigo",
            "titulo": "🔴 Renda quase toda comprometida",
            "descricao": (
                f"{comp:.0f}% da renda está comprometida. "
                "Qualquer imprevisto pode gerar inadimplência."
            ),
        })
    elif comp >= 70:
        alertas.append({
            "tipo": "perigo",
            "titulo": "🔴 Comprometimento de renda elevado",
            "descricao": (
                f"{comp:.0f}% da sua renda já está comprometida. "
                "Priorize quitar dívidas com juros altos e evite novos créditos."
            ),
        })
    elif comp >= 50:
        alertas.append({
            "tipo": "aviso",
            "titulo": "🟡 Atenção ao comprometimento de renda",
            "descricao": (
                f"{comp:.0f}% da sua renda está comprometida. "
                "Evite parcelar novas compras e tente reduzir gastos variáveis."
            ),
        })

    # ── Reserva de emergência ─────────────────────────────────────────────
    if renda > 0 and 0 < saldo < renda * 0.10:
        alertas.append({
            "tipo": "aviso",
            "titulo": "💰 Saldo livre muito baixo",
            "descricao": (
                f"Seu saldo livre (R$ {saldo:,.2f}) é menor que 10% da renda. "
                f"Tente guardar pelo menos R$ {renda * 0.10:,.2f}/mês como reserva."
            ),
        })

    # ── Situação saudável ─────────────────────────────────────────────────
    if nivel == "baixo" and saldo >= renda * 0.20:
        alertas.append({
            "tipo": "info",
            "titulo": "✅ Situação financeira saudável",
            "descricao": (
                "Parabéns! Suas finanças estão equilibradas. "
                "Continue monitorando e fortaleça sua reserva de emergência."
            ),
        })
    elif nivel == "baixo":
        alertas.append({
            "tipo": "info",
            "titulo": "✅ Risco controlado",
            "descricao": (
                "Seu perfil financeiro está dentro dos limites saudáveis. "
                "Mantenha o controle dos gastos e acompanhe mês a mês."
            ),
        })

    return alertas


def gerar_sugestoes(resultado: ResultadoRisco) -> list[str]:
    """
    Retorna lista de sugestões de ações concretas baseadas no nível de risco.
    Máximo de 5 sugestões para não sobrecarregar o usuário.
    """
    nivel = resultado.nivel
    comp  = resultado.comprometimento

    base = [
        "Registre todos os gastos, mesmo os pequenos — o controle começa pela visibilidade.",
    ]

    if nivel == "baixo":
        return base + [
            "Aumente gradualmente sua reserva de emergência para 3 a 6 meses de despesas.",
            "Revise assinaturas e serviços recorrentes que você não usa mais.",
            "Considere investimentos de renda fixa para o saldo livre mensal.",
        ]

    if nivel == "medio":
        return base + [
            f"Identifique os 3 maiores gastos variáveis e tente reduzi-los em 20%.",
            "Evite parcelar compras não essenciais nos próximos 3 meses.",
            "Priorize quitar a dívida com maior taxa de juros (método avalanche).",
            "Construa uma reserva mínima de R$ 500 antes de quitar dívidas antigas.",
        ]

    if nivel == "alto":
        return [
            "Corte imediatamente gastos com lazer, assinaturas e vestuário.",
            "Entre em contato com credores para renegociar prazos e reduzir juros.",
            "Busque fontes de renda extra: freelance, venda de itens não utilizados.",
            "Não assuma nenhuma nova dívida enquanto o índice de risco estiver alto.",
            "Procure orientação no Procon ou Serasa para renegociação coletiva.",
        ]

    if nivel == "critico":
        return [
            "PRIORIDADE: pague apenas alimentação, moradia, saúde e luz.",
            "Procure imediatamente um serviço de orientação ao superendividado (Procon, Serasa).",
            "A Lei 14.181/2021 garante renegociação com proteção ao mínimo existencial — use.",
            "Reúna todos os credores e proponha um plano único de pagamento.",
            "Não tome novos empréstimos para pagar dívidas antigas — isso aprofunda o problema.",
        ]

    return base


def gerar_sugestoes_por_categoria(gastos_cat: dict[str, float],
                                   renda: float) -> list[dict]:
    """
    Sugestões específicas por categoria de gasto quando o gasto
    ultrapassa proporções recomendadas da renda.

    Retorna lista de {categoria, pct_atual, pct_recomendado, sugestao}.
    """
    if renda <= 0:
        return []

    limites = {
        "Alimentação": 0.25,
        "Moradia":     0.30,
        "Transporte":  0.15,
        "Lazer":       0.10,
        "Vestuário":   0.05,
    }

    alertas_cat = []
    for cat, limite in limites.items():
        gasto = gastos_cat.get(cat, 0.0)
        pct   = gasto / renda
        if pct > limite:
            alertas_cat.append({
                "categoria":        cat,
                "pct_atual":        pct * 100,
                "pct_recomendado":  limite * 100,
                "valor_excedente":  (pct - limite) * renda,
                "sugestao": (
                    f"{cat}: você gastou {pct*100:.1f}% da renda "
                    f"(recomendado: até {limite*100:.0f}%). "
                    f"Reduza em R$ {(pct - limite) * renda:,.2f} para ficar no limite."
                ),
            })

    return alertas_cat
