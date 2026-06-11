"""
Página 01 — Dashboard principal
"""
import streamlit as st
from datetime import date
import plotly.graph_objects as go
import plotly.express as px

from modules.financeiro import (
    total_renda, total_gastos, total_parcelas_mensais,
    gastos_por_categoria, listar_dividas,
)
from modules.ia_engine import calcular_risco, NIVEL_LABEL, NIVEL_COR, NIVEL_BG
from modules.alertas import gerar_alertas, gerar_sugestoes
from modules.conteudo import obter_dicas


def render():
    uid  = st.session_state.user_id
    nome = st.session_state.username
    mes  = date.today().strftime("%Y-%m")

    st.markdown(f"## 🏠 Olá, {nome}!")
    st.markdown(f"<p style='color:#5A6A7A; margin-top:-0.5rem;'>Resumo de <b>{date.today().strftime('%B/%Y')}</b></p>",
                unsafe_allow_html=True)

    # ── Dados ────────────────────────────────────────────────────────────
    renda      = total_renda(uid, mes)
    gastos     = total_gastos(uid, mes)
    parcelas   = total_parcelas_mensais(uid)
    dividas    = listar_dividas(uid)
    gast_cat   = gastos_por_categoria(uid, mes)
    resultado  = calcular_risco(renda, gastos, parcelas, len(dividas))

    # ── Cartões de métricas ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _metrica("💰 Renda", f"R$ {renda:,.2f}", cor="#2D7D46")
    with c2:
        cor_g = "#C0392B" if gastos > renda else "#1A2744"
        _metrica("💸 Gastos", f"R$ {gastos:,.2f}", cor=cor_g)
    with c3:
        _metrica("📋 Parcelas", f"R$ {parcelas:,.2f}", cor="#E05C2A" if parcelas > 0 else "#1A2744")
    with c4:
        saldo = renda - gastos - parcelas
        _metrica("💵 Saldo livre", f"R$ {saldo:,.2f}", cor="#2D7D46" if saldo >= 0 else "#C0392B")

    st.markdown("<div style='margin:1rem 0'></div>", unsafe_allow_html=True)

    # ── Gauge de risco + Alertas ─────────────────────────────────────────
    col_gauge, col_alertas = st.columns([1, 1.6])

    with col_gauge:
        _gauge_risco(resultado)

    with col_alertas:
        st.markdown("<div class='section-title'>🔔 Alertas e recomendações</div>",
                    unsafe_allow_html=True)
        alertas = gerar_alertas(resultado, renda)
        for a in alertas:
            css = {"info": "alerta-verde", "aviso": "alerta-amarelo", "perigo": "alerta-vermelho"}[a["tipo"]]
            st.markdown(
                f"<div class='alerta-box {css}'><b>{a['titulo']}</b><br>{a['descricao']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Gráficos ─────────────────────────────────────────────────────────
    col_pizza, col_barras = st.columns(2)

    with col_pizza:
        st.markdown("<div class='section-title'>📊 Gastos por categoria</div>",
                    unsafe_allow_html=True)
        if gast_cat:
            fig = px.pie(
                names=list(gast_cat.keys()),
                values=list(gast_cat.values()),
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                legend=dict(font=dict(size=11)),
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_traces(textinfo="percent", hovertemplate="%{label}: R$ %{value:,.2f}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem gastos registrados neste mês.")

    with col_barras:
        st.markdown("<div class='section-title'>🧮 Composição financeira</div>",
                    unsafe_allow_html=True)
        _grafico_composicao(renda, gastos, parcelas)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sugestões corretivas ─────────────────────────────────────────────
    st.markdown("<div class='section-title'>💡 Sugestões para você</div>",
                unsafe_allow_html=True)
    sugestoes = gerar_sugestoes(resultado)
    for s in sugestoes:
        st.markdown(f"<div class='pi-card' style='padding:0.75rem 1rem; margin-bottom:0.5rem;'>• {s}</div>",
                    unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Conteúdo educativo ───────────────────────────────────────────────
    st.markdown("<div class='section-title'>📚 Para aprender mais</div>",
                unsafe_allow_html=True)
    dicas = obter_dicas(resultado.nivel, quantidade=3)
    cols_dicas = st.columns(len(dicas))
    for col, d in zip(cols_dicas, dicas):
        with col:
            st.markdown(
                f"""<div class='pi-card' style='height:100%;'>
                    <div style='font-size:1.5rem'>{d['emoji']}</div>
                    <div style='font-weight:600; margin:6px 0 4px;'>{d['titulo']}</div>
                    <div style='font-size:0.85rem; color:#5A6A7A;'>{d['corpo']}</div>
                </div>""",
                unsafe_allow_html=True,
            )


# ── Helpers visuais ──────────────────────────────────────────────────────────

def _metrica(label, valor, cor="#1A2744"):
    st.markdown(
        f"""<div class='pi-metric'>
            <div class='valor' style='color:{cor};'>{valor}</div>
            <div class='label'>{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def _gauge_risco(resultado):
    nivel  = resultado.nivel
    indice = resultado.indice
    cor    = NIVEL_COR[nivel]
    bg     = NIVEL_BG[nivel]
    label  = NIVEL_LABEL[nivel]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=indice,
        number={"suffix": " / 100", "font": {"size": 22, "color": cor}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#AAB4BE"},
            "bar": {"color": cor, "thickness": 0.3},
            "bgcolor": "white",
            "steps": [
                {"range": [0,  30], "color": "#E8F5E9"},
                {"range": [30, 55], "color": "#FEF3C7"},
                {"range": [55, 80], "color": "#FEE2D5"},
                {"range": [80,100], "color": "#FDEDEC"},
            ],
            "threshold": {"line": {"color": cor, "width": 4}, "value": indice},
        },
        title={"text": f"Índice de Risco<br><b>{label}</b>", "font": {"size": 14}},
    ))
    fig.update_layout(
        height=230,
        margin=dict(t=30, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#1A2744",
    )
    st.markdown("<div class='section-title'>📈 Índice de risco</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

    # Fatores ativados
    for f in resultado.fatores:
        if f["ativado"]:
            st.markdown(
                f"<div style='font-size:0.8rem; color:#C0392B; margin-bottom:3px;'>"
                f"⚠ {f['descricao']}</div>",
                unsafe_allow_html=True,
            )


def _grafico_composicao(renda, gastos, parcelas):
    saldo = max(renda - gastos - parcelas, 0)
    categorias = ["Gastos", "Parcelas dívidas", "Saldo livre"]
    valores    = [gastos, parcelas, saldo]
    cores      = ["#E05C2A", "#C0392B", "#2D7D46"]

    fig = go.Figure(go.Bar(
        x=categorias,
        y=valores,
        marker_color=cores,
        text=[f"R$ {v:,.0f}" for v in valores],
        textposition="outside",
    ))
    fig.add_hline(
        y=renda,
        line_dash="dash",
        line_color="#1A2744",
        annotation_text=f"Renda R$ {renda:,.0f}",
        annotation_position="top right",
    )
    fig.update_layout(
        height=260,
        margin=dict(t=20, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
