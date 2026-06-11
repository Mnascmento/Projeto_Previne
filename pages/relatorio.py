"""
Página 04 — Relatório financeiro mensal
"""
import streamlit as st
from datetime import date
import plotly.graph_objects as go
import plotly.express as px

from modules.financeiro import (
    total_renda, total_gastos, total_parcelas_mensais,
    gastos_por_categoria, listar_dividas, listar_gastos,
)
from modules.ia_engine import calcular_risco, NIVEL_LABEL, NIVEL_COR, NIVEL_BG
from modules.relatorio import gerar_relatorio_texto


def render():
    uid = st.session_state.user_id

    st.markdown("## 📊 Relatório Financeiro")
    st.markdown("<p style='color:#5A6A7A; margin-top:-0.5rem;'>Análise detalhada do seu mês financeiro.</p>",
                unsafe_allow_html=True)

    # Seletor de mês
    meses = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    col_m, col_a, _ = st.columns([2, 1, 3])

    with col_m:
        mes_num = st.selectbox(
        "Mês",
        range(1, 13),
        index=date.today().month - 1,
        format_func=lambda x: meses[x - 1]
    )

    with col_a:
        ano = st.selectbox(
        "Ano",
        range(2024, 2031),
        index=list(range(2024, 2031)).index(date.today().year)
    )

    # Formato para consultas no banco
    mes = f"{ano}-{mes_num:02d}"

    # Formato para exibição
    mes_label = f"{meses[mes_num - 1]} de {ano}"

    #col_m, _ = st.columns([1, 3])
    #with col_m:
    #    mes_dt = st.date_input(
    #        "Selecione o mês",
    #        value=date.today().replace(day=1),
    #        format="MM/YYYY",
    #    )
    #mes = mes_dt.strftime("%Y-%m")
    #mes_label = mes_dt.strftime("%B de %Y").capitalize()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Dados ─────────────────────────────────────────────────────────────
    renda    = total_renda(uid, mes)
    gastos   = total_gastos(uid, mes)
    parcelas = total_parcelas_mensais(uid)
    gast_cat = gastos_por_categoria(uid, mes)
    dividas  = listar_dividas(uid)
    gastos_l = listar_gastos(uid, mes)
    result   = calcular_risco(renda, gastos, parcelas, len(dividas))

    nivel_label = NIVEL_LABEL[result.nivel]
    nivel_cor   = NIVEL_COR[result.nivel]
    nivel_bg    = NIVEL_BG[result.nivel]

    # ── Cabeçalho do relatório ────────────────────────────────────────────
    st.markdown(
        f"""<div class='pi-card' style='display:flex; justify-content:space-between; align-items:center;
                    border-left:5px solid {nivel_cor}; padding:1.25rem 1.5rem;'>
            <div>
                <div style='font-size:0.8rem; color:#5A6A7A;'>Relatório de</div>
                <div style='font-size:1.3rem; font-weight:800; color:#1A2744;'>{mes_label}</div>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:0.78rem; color:#5A6A7A;'>Índice de risco</div>
                <div style='font-size:1.8rem; font-weight:800; color:{nivel_cor};'>
                    {result.indice:.0f}<span style='font-size:0.9rem;'>/100</span>
                </div>
                <div style='background:{nivel_bg}; color:{nivel_cor}; padding:2px 10px;
                            border-radius:20px; font-size:0.8rem; font-weight:600;'>
                    {nivel_label}
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin:1rem 0'></div>", unsafe_allow_html=True)

    # ── Resumo em 4 métricas ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    saldo = renda - gastos - parcelas
    _met(c1, "Renda total",      f"R$ {renda:,.2f}",    "#2D7D46")
    _met(c2, "Total de gastos",  f"R$ {gastos:,.2f}",   "#E05C2A")
    _met(c3, "Parcelas dívidas", f"R$ {parcelas:,.2f}", "#C0392B")
    _met(c4, "Saldo livre",      f"R$ {saldo:,.2f}",    "#2D7D46" if saldo >= 0 else "#C0392B")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("<div class='section-title'>🥧 Distribuição de gastos</div>",
                    unsafe_allow_html=True)
        if gast_cat:
            fig = px.pie(
                names=list(gast_cat.keys()),
                values=list(gast_cat.values()),
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_layout(height=280, margin=dict(t=0,b=0,l=0,r=0),
                              paper_bgcolor="rgba(0,0,0,0)")
            fig.update_traces(textinfo="label+percent",
                              hovertemplate="%{label}: R$ %{value:,.2f}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem gastos registrados.")

    with col_g2:
        st.markdown("<div class='section-title'>📉 Fatores de risco</div>",
                    unsafe_allow_html=True)
        detalhes_ativos = [
    d for d in result.detalhes
    if d.contribuicao > 0
]

        if detalhes_ativos:
            fig2 = go.Figure(go.Bar(
                y=[d.motivo[:40] if d.motivo else d.nome for d in detalhes_ativos],
                x=[d.contribuicao for d in detalhes_ativos],
                orientation="h",
                marker_color=nivel_cor,
                text=[f"{d.contribuicao:.1f} pts" for d in detalhes_ativos],
                textposition="outside",
            ))
            fig2.update_layout(
                height=280, margin=dict(t=0,b=0,l=0,r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.success("Nenhum fator de risco ativado! 🎉")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Tabela de gastos ──────────────────────────────────────────────────
    st.markdown("<div class='section-title'>🧾 Extrato de gastos</div>",
                unsafe_allow_html=True)
    if gastos_l:
        import pandas as pd
        df = pd.DataFrame(gastos_l)[["data", "descricao", "categoria", "valor"]]
        df.columns = ["Data", "Descrição", "Categoria", "Valor (R$)"]
        df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m/%Y")
        df["Valor (R$)"] = df["Valor (R$)"].map(lambda v: f"R$ {v:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem gastos registrados neste mês.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Download do relatório ─────────────────────────────────────────────
    st.markdown("<div class='section-title'>⬇️ Exportar relatório</div>",
                unsafe_allow_html=True)

    relatorio_txt = gerar_relatorio_texto(
        username=st.session_state.username,
        mes=mes,
        renda_total=renda,
        total_gastos=gastos,
        total_parcelas=parcelas,
        gastos_por_cat=gast_cat,
        dividas=dividas,
        resultado=result,
    )

    st.download_button(
        label="📥 Baixar relatório (.txt)",
        data=relatorio_txt.encode("utf-8"),
        file_name=f"relatorio_previsao_{mes}.txt",
        mime="text/plain",
        type="primary",
    )

    with st.expander("👁 Visualizar relatório"):
        st.code(relatorio_txt, language=None)


# ── Helper ────────────────────────────────────────────────────────────────────

def _met(col, label, valor, cor):
    with col:
        st.markdown(
            f"""<div class='pi-metric'>
                <div class='valor' style='color:{cor};'>{valor}</div>
                <div class='label'>{label}</div>
            </div>""",
            unsafe_allow_html=True,
        )
