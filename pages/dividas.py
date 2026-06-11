"""
Página 03 — Gestão de Dívidas
"""
import streamlit as st
import plotly.express as px

from modules.financeiro import (
    inserir_divida, listar_dividas,
    encerrar_divida, deletar_divida,
    total_parcelas_mensais,
)


def render():
    uid = st.session_state.user_id
    st.markdown("## 📋 Dívidas")
    st.markdown("<p style='color:#5A6A7A; margin-top:-0.5rem;'>Controle todas as suas dívidas e parcelas.</p>",
                unsafe_allow_html=True)

    # ── Formulário nova dívida ────────────────────────────────────────────
    with st.expander("➕ Cadastrar nova dívida", expanded=False):
        with st.form("form_divida", clear_on_submit=True):
            desc = st.text_input("Descrição", placeholder="Ex: Financiamento, Cartão Nubank")

            c1, c2, c3 = st.columns(3)
            with c1:
                val_total  = st.number_input("Valor total (R$)", min_value=0.01, step=100.0, format="%.2f")
            with c2:
                val_parc   = st.number_input("Valor da parcela (R$)", min_value=0.01, step=50.0, format="%.2f")
            with c3:
                parc_rest  = st.number_input("Parcelas restantes", min_value=1, step=1, value=12)

            c4, c5 = st.columns(2)
            with c4:
                taxa       = st.number_input("Taxa de juros (% a.m.)", min_value=0.0, step=0.1, format="%.2f",
                                             help="Informe 0 se não souber ou não houver juros.")
            with c5:
                vencimento = st.number_input("Dia de vencimento", min_value=1, max_value=31, value=10)

            ok = st.form_submit_button("Salvar dívida", type="primary")

        if ok:
            if not desc:
                st.warning("Informe uma descrição.")
            elif val_parc <= 0:
                st.warning("O valor da parcela deve ser maior que zero.")
            else:
                inserir_divida(uid, desc, val_total, val_parc, parc_rest, taxa, str(vencimento))
                st.success("Dívida cadastrada!")
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Lista de dívidas ativas ───────────────────────────────────────────
    dividas = listar_dividas(uid, apenas_ativas=True)
    total_p = total_parcelas_mensais(uid)

    if dividas:
        st.markdown(
            f"<div style='margin-bottom:1rem;'>"
            f"<span style='color:#5A6A7A; font-size:0.9rem;'>Parcelas mensais totais: </span>"
            f"<b style='color:#C0392B; font-size:1.1rem;'>R$ {total_p:,.2f}</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Gráfico de distribuição das parcelas
        if len(dividas) > 1:
            fig = px.bar(
                x=[d["descricao"][:20] for d in dividas],
                y=[d["valor_parcela"] for d in dividas],
                color=[d["taxa_juros"] for d in dividas],
                color_continuous_scale=["#2D7D46", "#F59E0B", "#C0392B"],
                labels={"x": "Dívida", "y": "Parcela (R$)", "color": "Juros % a.m."},
                text=[f"R$ {d['valor_parcela']:,.0f}" for d in dividas],
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=220,
                margin=dict(t=10, b=0, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Cards de dívidas
        st.markdown("<div class='section-title'>Dívidas ativas</div>", unsafe_allow_html=True)

        for d in dividas:
            with st.container():
                c_info, c_acoes = st.columns([4, 1])
                with c_info:
                    total_restante = d["valor_parcela"] * d["parcelas_restantes"]
                    progresso = 1 - (total_restante / d["valor_total"]) if d["valor_total"] > 0 else 0
                    progresso = max(0, min(1, progresso))

                    taxa_str = f"{d['taxa_juros']:.1f}% a.m." if d["taxa_juros"] > 0 else "sem juros"
                    venc_str = f"dia {d['vencimento']}" if d["vencimento"] else "—"

                    st.markdown(
                        f"""<div class='pi-card' style='padding:1rem 1.25rem;'>
                            <div style='display:flex; justify-content:space-between; align-items:center;'>
                                <div>
                                    <span style='font-weight:700; font-size:1rem;'>{d['descricao']}</span>
                                    <span style='margin-left:10px; font-size:0.78rem; color:#5A6A7A;'>
                                        Vence {venc_str} · {taxa_str}
                                    </span>
                                </div>
                                <div style='text-align:right;'>
                                    <span style='font-size:1.1rem; font-weight:700; color:#C0392B;'>
                                        R$ {d['valor_parcela']:,.2f}/mês
                                    </span><br>
                                    <span style='font-size:0.8rem; color:#5A6A7A;'>
                                        {d['parcelas_restantes']}x restantes · total R$ {total_restante:,.2f}
                                    </span>
                                </div>
                            </div>
                            <div style='margin-top:0.6rem; background:#E2E6EA; border-radius:10px; height:6px;'>
                                <div style='width:{progresso*100:.0f}%; background:#2D7D46; height:6px; border-radius:10px;'></div>
                            </div>
                            <div style='font-size:0.75rem; color:#5A6A7A; margin-top:3px;'>
                                {progresso*100:.0f}% pago do valor original
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with c_acoes:
                    st.markdown("<div style='margin-top:0.6rem'></div>", unsafe_allow_html=True)
                    if st.button("✅ Quitada", key=f"enc_{d['id']}", help="Marcar como quitada",
                                 use_container_width=True):
                        encerrar_divida(d["id"])
                        st.success("Dívida marcada como quitada!")
                        st.rerun()
                    if st.button("🗑 Remover", key=f"del_d_{d['id']}", help="Excluir dívida",
                                 use_container_width=True):
                        deletar_divida(d["id"])
                        st.rerun()

        # Dívidas encerradas
        with st.expander("Ver dívidas quitadas"):
            enc = listar_dividas(uid, apenas_ativas=False)
            enc = [d for d in enc if not d["ativa"]]
            if enc:
                for d in enc:
                    st.markdown(
                        f"<div style='color:#5A6A7A; font-size:0.9rem; padding:4px 0;'>"
                        f"✅ {d['descricao']} — R$ {d['valor_parcela']:,.2f}/mês (encerrada)</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.write("Nenhuma dívida quitada ainda.")

    else:
        st.markdown("""
        <div class='pi-card' style='text-align:center; padding:2rem;'>
            <div style='font-size:2rem;'>🎉</div>
            <div style='font-weight:700; margin-top:0.5rem;'>Nenhuma dívida ativa!</div>
            <div style='color:#5A6A7A; margin-top:0.25rem;'>
                Cadastre uma dívida acima caso tenha parcelas pendentes.
            </div>
        </div>
        """, unsafe_allow_html=True)
