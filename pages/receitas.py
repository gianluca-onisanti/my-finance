"""Página de gerenciamento de Receitas."""

import streamlit as st
import pandas as pd
import data_manager as dm
from datetime import date, datetime

st.title("💵 Receitas")
st.markdown("---")

categorias_receita = dm.load_categorias_receita()

# Formulário de cadastro
with st.expander("➕ Adicionar Nova Receita", expanded=False):
    with st.form("form_receita", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descrição *", placeholder="Ex: Salário CLT")
            valor = st.number_input("Valor (R$) *", min_value=0.01, step=100.0, format="%.2f")
        with col2:
            categoria = st.selectbox("Categoria", categorias_receita)
            data_inicio = st.date_input("Data de início", value=date.today())

        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            frequencia = st.selectbox("Frequência", list(dm.FREQUENCIAS.keys()))

        submitted = st.form_submit_button("Salvar Receita", width="stretch", type="primary")
        if submitted:
            if not descricao.strip():
                st.error("Preencha a descrição.")
            else:
                dm.add_receita(descricao, valor, frequencia, categoria, data_inicio.isoformat())
                st.success(f"Receita '{descricao}' cadastrada!")
                st.rerun()

# Lista de receitas
st.markdown("### Suas Receitas")

# Filtros
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtro_status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"], key="filtro_status_rec")
with col_f2:
    filtro_cat = st.selectbox("Categoria", ["Todas"] + categorias_receita, key="filtro_cat_rec")
with col_f3:
    filtro_freq = st.selectbox("Frequência", ["Todas"] + list(dm.FREQUENCIAS.keys()), key="filtro_freq_rec")

df = dm.load_receitas()

if df.empty:
    st.info("Nenhuma receita cadastrada. Use o formulário acima para adicionar.")
else:
    # Aplicar filtros
    if filtro_status == "Ativos":
        df = df[df["ativo"] == True]
    elif filtro_status == "Inativos":
        df = df[df["ativo"] == False]
    if filtro_cat != "Todas":
        df = df[df["categoria"] == filtro_cat]
    if filtro_freq != "Todas":
        df = df[df["frequencia"] == filtro_freq]

    if df.empty:
        st.warning("Nenhum resultado para os filtros selecionados.")
    else:
        # Totalizador
        total_mensal_filtrado = sum(
            dm.valor_mensal(row["valor"], row["frequencia"])
            for _, row in df[df["ativo"] == True].iterrows()
        )
        st.markdown(f"**Total mensal (filtrado, ativos): R$ {total_mensal_filtrado:,.2f}**")

        for _, row in df.iterrows():
            row_id = int(row["id"])
            ativo = row["ativo"]
            status_icon = "✅" if ativo else "⛔"
            mensal = dm.valor_mensal(row["valor"], row["frequencia"])

            with st.container():
                c1, c2, c3, c_menu = st.columns([4, 2, 2, 0.5])
                with c1:
                    st.markdown(f"{status_icon} **{row['descricao']}**")
                    st.caption(f"{row['categoria']} • {row['frequencia']} • Desde {row['data_inicio']}")
                with c2:
                    st.markdown(f"**R$ {row['valor']:,.2f}**")
                    st.caption("Valor cadastrado")
                with c3:
                    st.markdown(f"**R$ {mensal:,.2f}/mês**")
                    st.caption("Equivalente mensal")
                with c_menu:
                    with st.popover("⋮"):
                        label_toggle = "❌ Desativar" if ativo else "✅ Ativar"
                        if st.button(label_toggle, key=f"toggle_rec_{row_id}", width="stretch"):
                            dm.toggle_receita(row_id)
                            st.rerun()
                        if st.button("✏️ Editar", key=f"edit_rec_{row_id}", width="stretch"):
                            st.session_state[f"editing_rec_{row_id}"] = True
                            st.rerun()
                        if st.button("🗑️ Excluir", key=f"del_rec_{row_id}", width="stretch"):
                            st.session_state[f"confirm_del_rec_{row_id}"] = True
                            st.rerun()

                if st.session_state.get(f"confirm_del_rec_{row_id}", False):
                    st.warning(f"Confirma exclusão de '{row['descricao']}'?")
                    cc1, cc2, _ = st.columns([1, 1, 4])
                    with cc1:
                        if st.button("Sim, excluir", key=f"yes_del_rec_{row_id}", width="stretch"):
                            dm.delete_receita(row_id)
                            del st.session_state[f"confirm_del_rec_{row_id}"]
                            st.rerun()
                    with cc2:
                        if st.button("Cancelar", key=f"no_del_rec_{row_id}", width="stretch"):
                            del st.session_state[f"confirm_del_rec_{row_id}"]
                            st.rerun()

                # Formulário de edição inline
                if st.session_state.get(f"editing_rec_{row_id}", False):
                    with st.form(f"form_edit_rec_{row_id}"):
                        st.markdown("**Editando registro**")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            edit_desc = st.text_input("Descrição", value=row["descricao"], key=f"ed_desc_{row_id}")
                            edit_valor = st.number_input("Valor (R$)", min_value=0.01, value=float(row["valor"]),
                                                          step=100.0, format="%.2f", key=f"ed_val_{row_id}")
                        with ec2:
                            cat_index = categorias_receita.index(row["categoria"]) if row["categoria"] in categorias_receita else 0
                            edit_cat = st.selectbox("Categoria", categorias_receita, index=cat_index,
                                                     key=f"ed_cat_{row_id}")
                            try:
                                dt_val = datetime.strptime(row["data_inicio"], "%Y-%m-%d").date()
                            except (ValueError, TypeError):
                                dt_val = date.today()
                            edit_data = st.date_input("Data de início", value=dt_val, key=f"ed_data_{row_id}")

                        _, ec_center, _ = st.columns([1, 2, 1])
                        with ec_center:
                            edit_freq = st.selectbox("Frequência", list(dm.FREQUENCIAS.keys()),
                                                      index=list(dm.FREQUENCIAS.keys()).index(row["frequencia"])
                                                      if row["frequencia"] in dm.FREQUENCIAS else 0,
                                                      key=f"ed_freq_{row_id}")

                        bc1, bc2 = st.columns(2)
                        with bc1:
                            if st.form_submit_button("💾 Salvar", width="stretch", type="primary"):
                                dm.update_receita(row_id,
                                                   descricao=edit_desc, valor=edit_valor,
                                                   frequencia=edit_freq, categoria=edit_cat,
                                                   data_inicio=edit_data.isoformat())
                                del st.session_state[f"editing_rec_{row_id}"]
                                st.rerun()
                        with bc2:
                            if st.form_submit_button("Cancelar", width="stretch"):
                                del st.session_state[f"editing_rec_{row_id}"]
                                st.rerun()

                st.markdown("---")
