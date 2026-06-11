import streamlit as st
from modules.auth import init_db, login_page, register_page

# ── Configuração global da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Previsão Inteligente",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Paleta e variáveis */
:root {
    --verde-safe:  #2D7D46;
    --verde-light: #E8F5E9;
    --amarelo:     #F59E0B;
    --amarelo-light: #FEF3C7;
    --vermelho:    #C0392B;
    --vermelho-light: #FDEDEC;
    --azul-dark:   #1A2744;
    --cinza-bg:    #F7F8FA;
    --cinza-card:  #FFFFFF;
    --cinza-borda: #E2E6EA;
    --texto-prim:  #1A2744;
    --texto-sec:   #5A6A7A;
}

/* Reset geral */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

/* Fundo principal */
.stApp { 
    background-color: var(--cinza-bg); 
    color: var(--texto-prim);
        }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--azul-dark) !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #CBD5E1 !important;
    font-size: 0.9rem;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}       
[data-testid="stSidebarNav"] {
    display: none;
}
            
/* Label */
label[data-testid="stWidgetLabel"] {
    color: var(--texto-prim) !important;
    font-weight: 600 !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: var(--texto-prim) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--vermelho) !important;
    font-weight: 600 !important;
}

/* Expander de Forms */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {
    color: var(--texto-prim) !important;
    font-weight: 600 !important;
}

/* Cards genéricos */
.pi-card {
    background: var(--cinza-card);
    border: 1px solid var(--cinza-borda);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

/* Badges de risco */
.badge-baixo  { background:#E8F5E9; color:#2D7D46; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600; }
.badge-medio  { background:#FEF3C7; color:#92400E; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600; }
.badge-alto   { background:#FDEDEC; color:#C0392B; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600; }
.badge-critico{ background:#C0392B; color:#FFFFFF;  padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600; }

/* Métrica customizada */
.pi-metric {
    background: var(--cinza-card);
    border: 1px solid var(--cinza-borda);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.pi-metric .valor {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--texto-prim);
    line-height: 1.2;
}
.pi-metric .label {
    font-size: 0.78rem;
    color: var(--texto-sec);
    margin-top: 4px;
}

/* Alertas */
.alerta-box {
    border-left: 4px solid;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.alerta-verde  { border-color:#2D7D46; background:#E8F5E9; color:#1B5E20; }
.alerta-amarelo{ border-color:#F59E0B; background:#FEF3C7; color:#78350F; }
.alerta-vermelho{ border-color:#C0392B; background:#FDEDEC; color:#7F1D1D; }

/* Botão primário */
.stButton > button[kind="primary"] {
    background: var(--verde-safe) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Títulos de seção */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--texto-prim);
    margin: 1.5rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Divider suave */
hr { border: none; border-top: 1px solid var(--cinza-borda); margin: 1.25rem 0; }

/* Ocultar menu padrão do Streamlit (opcional) */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Inicialização do banco ──────────────────────────────────────────────────
init_db()


# ── Roteamento de autenticação ─────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.user_id is None:
    # Tela de entrada: Login ou Cadastro
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem;">
        <span style="font-size:2.5rem;">💡</span>
        <h1 style="font-size:1.8rem; font-weight:800; color:#1A2744; margin:0.25rem 0;">
            Previsão Inteligente
        </h1>
        <p style="color:#5A6A7A; font-size:0.95rem;">
            Controle financeiro com IA preditiva de risco
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Entrar", "Criar conta"])
    with tab_login:
        login_page()
    with tab_register:
        register_page()

else:
    # ── Sidebar de navegação ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 0.5rem 0 1.5rem;">
            <div style="font-size:1.5rem; margin-bottom:4px;">💡</div>
            <div style="font-size:1rem; font-weight:700; color:#FFFFFF;">Previsão Inteligente</div>
            <div style="font-size:0.8rem; color:#94A3B8; margin-top:4px;">
                Olá, <b style="color:#E2E8F0;">{st.session_state.username}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pagina = st.radio(
            "Navegação",
            options=["🏠 Dashboard", "💸 Lançamentos", "📋 Dívidas", "📊 Relatório"],
            label_visibility="collapsed",
        )

        st.markdown("<hr style='border-color:#2D3F5A; margin: 1rem 0;'>", unsafe_allow_html=True)

        if st.button("Sair", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = ""
            st.rerun()

    # ── Roteamento de páginas ──────────────────────────────────────────────
    if pagina == "🏠 Dashboard":
        import pages.dashboard as pg
        pg.render()
    elif pagina == "💸 Lançamentos":
        import pages.lancamentos as pg
        pg.render()
    elif pagina == "📋 Dívidas":
        import pages.dividas as pg
        pg.render()
    elif pagina == "📊 Relatório":
        import pages.relatorio as pg
        pg.render()
