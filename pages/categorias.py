"""Página de gerenciamento de Categorias."""

import streamlit as st
import data_manager as dm

st.title("🏷️ Categorias")
st.markdown("---")

col_rec, col_desp = st.columns(2)

# --- Categorias de Receita ---
with col_rec:
    st.subheader("Categorias de Receita")

    cats_receita = dm.load_categorias_receita()

    with st.form("form_add_cat_receita", clear_on_submit=True):
        nova_cat = st.text_input("Nova categoria", placeholder="Ex: Dividendos", key="nova_cat_rec")
        if st.form_submit_button("➕ Adicionar", width="stretch"):
            if nova_cat.strip():
                if nova_cat.strip() in cats_receita:
                    st.warning("Essa categoria já existe.")
                else:
                    dm.add_categoria_receita(nova_cat.strip())
                    st.success(f"Categoria '{nova_cat.strip()}' adicionada!")
                    st.rerun()
            else:
                st.error("Digite um nome para a categoria.")

    for cat in cats_receita:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"• {cat}")
        with c2:
            if st.button("🗑️", key=f"del_cat_rec_{cat}", width="stretch"):
                # Verificar se está em uso
                receitas = dm.load_receitas()
                em_uso = not receitas[receitas["categoria"] == cat].empty if not receitas.empty else False
                if em_uso:
                    st.warning(f"'{cat}' está em uso!")
                else:
                    dm.delete_categoria_receita(cat)
                    st.rerun()

# --- Categorias de Despesa ---
with col_desp:
    st.subheader("Categorias de Despesa")

    cats_despesa = dm.load_categorias_despesa()

    with st.form("form_add_cat_despesa", clear_on_submit=True):
        nova_cat = st.text_input("Nova categoria", placeholder="Ex: Delivery", key="nova_cat_desp")
        if st.form_submit_button("➕ Adicionar", width="stretch"):
            if nova_cat.strip():
                if nova_cat.strip() in cats_despesa:
                    st.warning("Essa categoria já existe.")
                else:
                    dm.add_categoria_despesa(nova_cat.strip())
                    st.success(f"Categoria '{nova_cat.strip()}' adicionada!")
                    st.rerun()
            else:
                st.error("Digite um nome para a categoria.")

    for cat in cats_despesa:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"• {cat}")
        with c2:
            if st.button("🗑️", key=f"del_cat_desp_{cat}", width="stretch"):
                despesas = dm.load_despesas()
                em_uso = not despesas[despesas["categoria"] == cat].empty if not despesas.empty else False
                if em_uso:
                    st.warning(f"'{cat}' está em uso!")
                else:
                    dm.delete_categoria_despesa(cat)
                    st.rerun()
