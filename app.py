"""My Finance - Aplicativo de Finanças Pessoais."""

import streamlit as st

st.set_page_config(
    page_title="My Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
    }
    .metric-positive { color: #00c853; font-weight: bold; }
    .metric-negative { color: #ff5252; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Navegação
paginas = {
    "Dashboard": "pages/dashboard.py",
    "Receitas": "pages/receitas.py",
    "Despesas": "pages/despesas.py",
    "Relatórios": "pages/relatorios.py",
    "Metas": "pages/metas.py",
    "Categorias": "pages/categorias.py",
}

st.sidebar.title("💰 My Finance")
st.sidebar.markdown("---")
pagina_selecionada = st.sidebar.radio(
    "Navegação",
    list(paginas.keys()),
    label_visibility="collapsed",
)
st.sidebar.markdown("---")

# Exportar dados
import data_manager as dm
import tempfile
import os

st.sidebar.markdown("### Ferramentas")
if st.sidebar.button("📥 Exportar para Excel", width="stretch"):
    filepath = os.path.join(tempfile.gettempdir(), "my_finance_export.xlsx")
    dm.exportar_xlsx(filepath)
    with open(filepath, "rb") as f:
        st.sidebar.download_button(
            label="⬇️ Baixar arquivo .xlsx",
            data=f,
            file_name="my_finance_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

# Executar página selecionada
page_file = paginas[pagina_selecionada]
page_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), page_file)
with open(page_path, "r", encoding="utf-8") as f:
    exec(f.read())
