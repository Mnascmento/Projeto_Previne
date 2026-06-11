"""
modules/ia_engine.py

Motor de IA preditiva de risco de superendividamento.
Implementação: sistema de pontuação com pesos por feature.

Justificativa acadêmica (conforme discutido no projeto):
  Regras ponderadas foram preferidas ao ML supervisionado porque:
  1. Não há dados históricos reais rotulados disponíveis no protótipo.
  2. O modelo é completamente explicável — cada ponto tem uma razão.
  3. Os limiares foram calibrados com base nos dados do Banco Central
     do Brasil (Relatório de Economia Bancária) e na literatura sobre
     superendividamento (lei 14.181/2021 e PEIC/CNC).
  4. A arquitetura permite substituição futura por modelo scikit-learn
     sem mudar a interface da função principal.

Índice de risco: 0 a 100
  0–29  → baixo    (🟢 situação saudável)
  30–54 → medio    (🟡 atenção necessária)
  55–79 → alto     (🔴 risco elevado)
  80–100→ critico  (⛔ superendividamento iminente)

Features (pesos somam 1.0):
  comprometimento  0.40  — % da renda comprometida com gastos + parcelas
  num_dividas      0.20  — quantidade de dívidas ativas
  maior_juros      0.25  — taxa da dívida mais cara (proxy de desespero)
  atrasos          0.10  — comportamento de pagamento (stub = 0 no protótipo)
  historico        0.05  — penalidade por dados insuficientes
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ── Configuração de pesos ─────────────────────────────────────────────────
# A soma deve ser sempre 1.0.
# Altere aqui sem tocar na lógica de cálculo.

PESOS: dict[str, float] = {
    "comprometimento": 0.40,
    "num_dividas":     0.20,
    "maior_juros":     0.25,
    "atrasos":         0.10,
    "historico":       0.05,
}

assert abs(sum(PESOS.values()) - 1.0) < 1e-9, (
    f"Soma dos pesos deve ser 1.0, mas é {sum(PESOS.values()):.4f}. "
    "Ajuste PESOS em ia_engine.py."
)


# ── Limiares de classificação ─────────────────────────────────────────────
# Lista de (limiar_mínimo, nível) em ordem decrescente.

NIVEIS: list[tuple[int, str]] = [
    (80, "critico"),
    (55, "alto"),
    (30, "medio"),
    (0,  "baixo"),
]


# ── Dataclasses ───────────────────────────────────────────────────────────

@dataclass
class DetalheFeature:
    nome:         str
    valor_bruto:  float        # valor real da feature (ex: 45.0 para 45%)
    score_norm:   float        # score normalizado 0–1 para esta feature
    peso:         float        # peso configurado
    contribuicao: float        # score_norm * peso * 100
    motivo:       str          # texto legível exibido ao usuário


@dataclass
class ResultadoRisco:
    indice:          float                      # 0–100
    nivel:           str                        # baixo|medio|alto|critico
    comprometimento: float                      # % da renda comprometida
    saldo_livre:     float                      # renda - gastos - parcelas
    detalhes:        list[DetalheFeature] = field(default_factory=list)
    motivos:         list[str]            = field(default_factory=list)
    fatores:         list[dict]           = field(default_factory=list)  #compatibilidade com módulos antigos


# ── Funções de score por feature ─────────────────────────────────────────
# Cada função recebe o valor bruto e retorna um float 0–1.

def _score_comprometimento(pct: float) -> float:
    """
    % da renda comprometida com gastos + parcelas.
    Referência: Banco Central — comprometimento > 30% = atenção,
    > 50% = risco, > 80% = crítico.
    """
    if pct >= 100: return 1.0
    if pct >= 80:  return 0.90
    if pct >= 60:  return 0.70
    if pct >= 50:  return 0.55
    if pct >= 30:  return 0.35
    if pct >= 20:  return 0.15
    return 0.05


def _score_num_dividas(qtd: int) -> float:
    """
    Número de dívidas ativas.
    Referência: CDC americano e literatura de crédito brasileira —
    3+ dívidas simultâneas elevam o risco de inadimplência.
    """
    if qtd >= 6: return 1.0
    if qtd == 5: return 0.85
    if qtd == 4: return 0.70
    if qtd == 3: return 0.50
    if qtd == 2: return 0.30
    if qtd == 1: return 0.15
    return 0.0


def _score_maior_juros(taxa_am: float) -> float:
    """
    Maior taxa de juros entre as dívidas ativas (% ao mês).
    Referência: BACEN — taxa do rotativo do cartão > 15% a.m. = crítico.
    Cheque especial > 8% a.m. = alto.
    """
    if taxa_am >= 15.0: return 1.0
    if taxa_am >= 10.0: return 0.85
    if taxa_am >= 8.0:  return 0.70
    if taxa_am >= 5.0:  return 0.50
    if taxa_am >= 2.0:  return 0.30
    if taxa_am >= 0.5:  return 0.10
    return 0.0


def _score_atrasos(qtd_atrasos: int) -> float:
    """
    Quantidade de parcelas em atraso.
    No protótipo este valor é sempre 0 (não rastreamos atrasos ainda).
    A estrutura está pronta para quando o dado estiver disponível.
    """
    if qtd_atrasos >= 5: return 1.0
    if qtd_atrasos >= 3: return 0.70
    if qtd_atrasos >= 1: return 0.40
    return 0.0


def _score_historico(meses_de_dados: int) -> float:
    """
    Penalidade por dados insuficientes.
    Usuário com menos de 2 meses de histórico recebe score máximo
    (não temos dados para confiar).
    Com mais histórico, o score diminui.
    """
    if meses_de_dados == 0: return 1.0
    if meses_de_dados == 1: return 0.70
    if meses_de_dados == 2: return 0.40
    if meses_de_dados >= 3: return 0.0
    return 0.0


# ── Função principal ──────────────────────────────────────────────────────

def calcular_risco(
    renda_total:      float,
    total_gastos:     float,
    total_parcelas:   float,
    qtd_dividas:      int,
    maior_taxa:       float = 0.0,
    qtd_atrasos:      int   = 0,
    meses_de_dados:   int   = 1,
) -> ResultadoRisco:
    """
    Calcula o índice de risco de superendividamento.

    Parâmetros:
        renda_total     — soma das rendas do mês (R$)
        total_gastos    — soma dos gastos do mês (R$)
        total_parcelas  — soma das parcelas mensais de dívidas ativas (R$)
        qtd_dividas     — número de dívidas ativas
        maior_taxa      — maior taxa de juros entre as dívidas (% a.m.)
        qtd_atrasos     — parcelas em atraso (stub = 0 no protótipo)
        meses_de_dados  — meses de histórico disponíveis

    Retorna:
        ResultadoRisco com indice (0–100), nivel, saldo_livre,
        comprometimento, detalhes por feature e motivos textuais.
    """
    # Caso sem renda cadastrada
    if renda_total <= 0:
        return ResultadoRisco(
            indice=100.0,
            nivel="critico",
            comprometimento=100.0,
            saldo_livre=-(total_gastos + total_parcelas),
            motivos=["Nenhuma renda cadastrada — impossível calcular comprometimento."],
            fatores=[
                {
                "descricao": "Nenhuma renda cadastrada",
                "peso": 100,
                "ativado": True,
                }
            ]
        )

    comprometimento = ((total_gastos + total_parcelas) / renda_total) * 100
    saldo_livre     = renda_total - total_gastos - total_parcelas

    # Calcular score normalizado por feature
    features = [
        ("comprometimento", comprometimento, _score_comprometimento(comprometimento)),
        ("num_dividas",     qtd_dividas,     _score_num_dividas(qtd_dividas)),
        ("maior_juros",     maior_taxa,      _score_maior_juros(maior_taxa)),
        ("atrasos",         qtd_atrasos,     _score_atrasos(qtd_atrasos)),
        ("historico",       meses_de_dados,  _score_historico(meses_de_dados)),
    ]

    detalhes: list[DetalheFeature] = []
    indice_total = 0.0

    for nome, val_bruto, score_norm in features:
        peso         = PESOS[nome]
        contribuicao = score_norm * peso * 100
        indice_total += contribuicao

        motivo = _gerar_motivo(nome, val_bruto, score_norm)
        detalhes.append(DetalheFeature(
            nome=nome,
            valor_bruto=val_bruto,
            score_norm=score_norm,
            peso=peso,
            contribuicao=contribuicao,
            motivo=motivo,
        ))

    indice = round(min(indice_total, 100.0), 1)
    nivel  = _classificar_nivel(indice)

    # Motivos legíveis: apenas features com contribuição > 2 pts
    motivos = [
        d.motivo for d in detalhes
        if d.contribuicao > 2.0 and d.motivo
    ]

    fatores = []

    for detalhe in detalhes:
        fatores.append({
        "descricao": detalhe.motivo,
        "peso": round(detalhe.contribuicao, 1),
        "ativado": detalhe.contribuicao > 0,
        })

    return ResultadoRisco(
        indice=indice,
        nivel=nivel,
        comprometimento=comprometimento,
        saldo_livre=saldo_livre,
        detalhes=detalhes,
        motivos=motivos,
        fatores=fatores
    )


# ── Helpers internos ──────────────────────────────────────────────────────

def _classificar_nivel(indice: float) -> str:
    for limiar, nivel in NIVEIS:
        if indice >= limiar:
            return nivel
    return "baixo"


def _gerar_motivo(nome: str, val_bruto: float, score_norm: float) -> str:
    if score_norm < 0.1:
        return ""  # feature não contribui — não exibir

    if nome == "comprometimento":
        return f"{val_bruto:.1f}% da renda comprometida com gastos e dívidas."
    if nome == "num_dividas":
        return f"{int(val_bruto)} dívida(s) ativa(s) no momento."
    if nome == "maior_juros" and val_bruto > 0:
        return f"Dívida com taxa de {val_bruto:.1f}% a.m. — custo financeiro elevado."
    if nome == "atrasos" and val_bruto > 0:
        return f"{int(val_bruto)} parcela(s) em atraso detectada(s)."
    if nome == "historico":
        return "Histórico financeiro insuficiente para análise completa."
    return ""


# ── Mapeamentos visuais exportados ────────────────────────────────────────

NIVEL_LABEL = {
    "baixo":   "🟢 Baixo",
    "medio":   "🟡 Médio",
    "alto":    "🔴 Alto",
    "critico": "⛔ Crítico",
}

NIVEL_COR = {
    "baixo":   "#2D7D46",
    "medio":   "#F59E0B",
    "alto":    "#E05C2A",
    "critico": "#C0392B",
}

NIVEL_BG = {
    "baixo":   "#E8F5E9",
    "medio":   "#FEF3C7",
    "alto":    "#FEE2D5",
    "critico": "#FDEDEC",
}
