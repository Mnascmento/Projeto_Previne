"""
Página 02 — Lançamentos (Renda e Gastos)
"""
import streamlit as st
from datetime import date

from modules.financeiro import (
    CATEGORIAS_GASTO,
    inserir_renda, listar_rendas, deletar_renda, total_renda,
    inserir_gasto, listar_gastos, deletar_gasto, total_gastos,
)


def render():
    uid = st.session_state.user_id
    st.markdown("## 💸 Lançamentos")
    st.markdown("<p style='color:#5A6A7A; margin-top:-0.5rem;'>Registre rendas e gastos do mês.</p>",
                unsafe_allow_html=True)

    # Seletor de mês
    meses = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    col1, col2 = st.columns(2)

    with col1:
        mes_num = st.selectbox(
        "Mês",
        range(1, 13),
        index=date.today().month - 1,
        format_func=lambda x: meses[x - 1]
        )

    with col2:
        ano = st.selectbox(
        "Ano",
        range(2024, 2031),
        index=2  # ajuste conforme necessário
        )

    mes = f"{ano}-{mes_num:02d}"
    # col_mes, _ = st.columns([1, 3])
    # with col_mes:
    #    mes_sel = st.date_input(
    #        "Mês de referência",
    #        value=date.today().replace(day=1),
    #        format="MM/YYYY",
    #        label_visibility="visible",
    #    )
    # mes = mes_sel.strftime("%Y-%m")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Abas Renda / Gastos ───────────────────────────────────────────────
    tab_renda, tab_gastos = st.tabs(["💰 Renda", "🛒 Gastos"])

    # ─── ABA RENDA ────────────────────────────────────────────────────────
    with tab_renda:
        st.markdown("<div class='section-title'>Nova fonte de renda</div>",
                    unsafe_allow_html=True)

        with st.form("form_renda", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                desc_r  = st.text_input("Descrição", placeholder="Ex: Salário, Freelance")
            with c2:
                valor_r = st.number_input("Valor (R$)", min_value=0.01, step=50.0, format="%.2f")
            with c3:
                tipo_r  = st.selectbox("Tipo", ["fixa", "variavel"],
                                       format_func=lambda x: "Fixa" if x == "fixa" else "Variável")
            ok_r = st.form_submit_button("➕ Adicionar renda", type="primary")

        if ok_r:
            if not desc_r:
                st.warning("Informe uma descrição.")
            else:
                inserir_renda(uid, desc_r, valor_r, tipo_r, mes)
                st.success("Renda adicionada!")
                st.rerun()

        # Listagem
        rendas = listar_rendas(uid, mes)
        tot_r  = total_renda(uid, mes)

        if rendas:
            st.markdown(
                f"<div style='color:#5A6A7A; font-size:0.85rem; margin-bottom:0.5rem;'>"
                f"Total no mês: <b style='color:#2D7D46; font-size:1rem;'>R$ {tot_r:,.2f}</b></div>",
                unsafe_allow_html=True,
            )
            for r in rendas:
                c_desc, c_tipo, c_val, c_del = st.columns([3, 1.2, 1.2, 0.5])
                with c_desc: st.write(r["descricao"])
                with c_tipo:
                    t = "🔁 Fixa" if r["tipo"] == "fixa" else "📈 Variável"
                    st.write(t)
                with c_val:
                    st.write(f"R$ {r['valor']:,.2f}")
                with c_del:
                    if st.button("🗑", key=f"del_r_{r['id']}", help="Remover"):
                        deletar_renda(r["id"])
                        st.rerun()
        else:
            st.info("Nenhuma renda cadastrada para este mês. Adicione acima!")

    # ─── ABA GASTOS ───────────────────────────────────────────────────────
    with tab_gastos:
        st.markdown("<div class='section-title'>Novo gasto</div>",
                    unsafe_allow_html=True)

        with st.form("form_gasto", clear_on_submit=True):
            c1, c2 = st.columns([2, 1])
            with c1:
                desc_g = st.text_input("Descrição", placeholder="Ex: Mercado, Combustível")
            with c2:
                cat_g  = st.selectbox("Categoria", CATEGORIAS_GASTO)

            c3, c4 = st.columns([1, 1])
            with c3:
                valor_g = st.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f")
            with c4:
                data_g  = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")

            ok_g = st.form_submit_button("➕ Registrar gasto", type="primary")

        if ok_g:
            if not desc_g:
                st.warning("Informe uma descrição.")
            else:
                inserir_gasto(uid, desc_g, cat_g, valor_g, data_g)
                st.success("Gasto registrado!")
                st.rerun()

        # Listagem
        gastos = listar_gastos(uid, mes)
        tot_g  = total_gastos(uid, mes)

        if gastos:
            st.markdown(
                f"<div style='color:#5A6A7A; font-size:0.85rem; margin-bottom:0.5rem;'>"
                f"Total no mês: <b style='color:#C0392B; font-size:1rem;'>R$ {tot_g:,.2f}</b></div>",
                unsafe_allow_html=True,
            )

            # Cabeçalho
            hc = st.columns([1.2, 2, 1.5, 1.2, 0.5])
            for h, t in zip(hc, ["Data", "Descrição", "Categoria", "Valor", ""]):
                h.markdown(f"<span style='font-size:0.78rem; color:#5A6A7A; font-weight:600;'>{t}</span>",
                           unsafe_allow_html=True)

            for g in gastos:
                c_data, c_desc, c_cat, c_val, c_del = st.columns([1.2, 2, 1.5, 1.2, 0.5])
                with c_data: st.write(g["data"][8:] + "/" + g["data"][5:7] + "/" + g["data"][:4])
                with c_desc: st.write(g["descricao"])
                with c_cat:  st.write(g["categoria"])
                with c_val:  st.write(f"R$ {g['valor']:,.2f}")
                with c_del:
                    if st.button("🗑", key=f"del_g_{g['id']}", help="Remover"):
                        deletar_gasto(g["id"])
                        st.rerun()
        else:
            st.info("Nenhum gasto registrado para este mês.")
