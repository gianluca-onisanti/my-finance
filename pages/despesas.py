"""Página de gerenciamento de Despesas."""

import streamlit as st
import pandas as pd
import data_manager as dm
from datetime import date, datetime

st.title("💸 Despesas")
st.markdown("---")

categorias_despesa = dm.load_categorias_despesa()

# Formulário de cadastro
with st.expander("➕ Adicionar Nova Despesa", expanded=False):
    with st.form("form_despesa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descrição *", placeholder="Ex: Aluguel")
            frequencia = st.selectbox(
                "Frequência",
                list(dm.FREQUENCIAS.keys()) + ["Parcelado"],
                help="Escolha 'Parcelado' para compras parceladas no cartão",
            )
            valor = st.number_input(
                "Valor total da compra (R$) *" if "Parcelado" else "Valor (R$) *",
                min_value=0.01, step=50.0, format="%.2f",
                help="Para parcelados, informe o valor TOTAL da compra (ex: R$ 2.000). O sistema calcula a parcela automaticamente.",
            )
            dia_vencimento = st.number_input(
                "Dia do vencimento (opcional)",
                min_value=0, max_value=31, value=0, step=1,
                help="Dia do mês em que a conta vence. 0 = sem vencimento.",
            )
        with col2:
            categoria = st.selectbox("Categoria", categorias_despesa)
            destinatario = st.text_input("Destinatário (opcional)", placeholder="Ex: Nubank, João, Casas Bahia",
                                          help="Para quem vai esse pagamento? Usado no gráfico de repasses.")
            data_inicio = st.date_input("Data de início", value=date.today())

        st.markdown("##### Parcelamento (se aplicável)")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            parcelas_total = st.number_input("Total de parcelas", min_value=0, value=0, step=1,
                                              help="0 = não parcelado")
        with col_p2:
            parcelas_pagas = st.number_input("Parcelas já pagas", min_value=0, value=0, step=1)
        with col_p3:
            if parcelas_total > 0 and valor > 0:
                st.metric("Valor da parcela", f"R$ {valor / parcelas_total:,.2f}")

        submitted = st.form_submit_button("Salvar Despesa", width="stretch", type="primary")
        if submitted:
            if not descricao.strip():
                st.error("Preencha a descrição.")
            elif frequencia == "Parcelado" and parcelas_total == 0:
                st.error("Para despesas parceladas, informe o total de parcelas.")
            else:
                # Se selecionou parcelas mas não escolheu "Parcelado", forçar frequência
                freq_final = frequencia
                if parcelas_total > 0 and frequencia != "Parcelado":
                    freq_final = "Parcelado"
                dm.add_despesa(
                    descricao=descricao,
                    valor=valor,
                    frequencia=freq_final,
                    categoria=categoria,
                    data_inicio=data_inicio.isoformat(),
                    dia_vencimento=dia_vencimento if dia_vencimento > 0 else None,
                    parcelas_total=parcelas_total if parcelas_total > 0 else None,
                    parcelas_pagas=parcelas_pagas if parcelas_total > 0 else None,
                    destinatario=destinatario.strip(),
                )
                st.success(f"Despesa '{descricao}' cadastrada!")
                st.rerun()

# Lista de despesas
st.markdown("### Suas Despesas")

# Filtros
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtro_status = st.selectbox("Status", ["Todos", "Ativos", "Inativos"], key="filtro_status_desp")
with col_f2:
    filtro_cat = st.selectbox("Categoria", ["Todas"] + categorias_despesa, key="filtro_cat_desp")
with col_f3:
    filtro_freq = st.selectbox(
        "Frequência", ["Todas"] + list(dm.FREQUENCIAS.keys()) + ["Parcelado"], key="filtro_freq_desp"
    )

df = dm.load_despesas()

if df.empty:
    st.info("Nenhuma despesa cadastrada. Use o formulário acima para adicionar.")
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
        total_mensal_filtrado = 0.0
        for _, row in df[df["ativo"] == True].iterrows():
            if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")) and pd.notna(row.get("parcelas_pagas")):
                if row["parcelas_pagas"] < row["parcelas_total"]:
                    total_mensal_filtrado += row["valor"] / row["parcelas_total"]
            else:
                total_mensal_filtrado += dm.valor_mensal(row["valor"], row["frequencia"])

        st.markdown(f"**Total mensal (filtrado, ativos): R$ {total_mensal_filtrado:,.2f}**")

        for _, row in df.iterrows():
            row_id = int(row["id"])
            ativo = row["ativo"]
            status_icon = "✅" if ativo else "⛔"

            # Calcular equivalente mensal
            if row["frequencia"] == "Parcelado":
                mensal = row["valor"] / row["parcelas_total"] if pd.notna(row.get("parcelas_total")) and row["parcelas_total"] > 0 else row["valor"]
                parcelas_info = ""
                if pd.notna(row.get("parcelas_total")):
                    pagas = int(row["parcelas_pagas"]) if pd.notna(row.get("parcelas_pagas")) else 0
                    total_p = int(row["parcelas_total"])
                    restantes = total_p - pagas
                    parcelas_info = f" • {pagas}/{total_p} parcelas (faltam {restantes})"
            else:
                mensal = dm.valor_mensal(row["valor"], row["frequencia"])
                parcelas_info = ""

            with st.container():
                c1, c2, c3, c_menu = st.columns([4, 2, 2, 0.5])
                with c1:
                    st.markdown(f"{status_icon} **{row['descricao']}**")
                    venc_text = f" • Vence dia {int(row['dia_vencimento']):02d}" if pd.notna(row.get("dia_vencimento")) else ""
                    dest_text = f" • → {row['destinatario']}" if pd.notna(row.get("destinatario")) and str(row.get("destinatario", "")).strip() else ""
                    st.caption(f"{row['categoria']} • {row['frequencia']}{venc_text}{dest_text}{parcelas_info}")

                    if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")):
                        pagas = int(row["parcelas_pagas"]) if pd.notna(row.get("parcelas_pagas")) else 0
                        total_p = int(row["parcelas_total"])
                        st.progress(pagas / total_p if total_p > 0 else 0, text=f"{pagas}/{total_p}")

                with c2:
                    st.markdown(f"**R$ {row['valor']:,.2f}**")
                    if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")) and row["parcelas_total"] > 0:
                        st.caption(f"Valor total ({int(row['parcelas_total'])}x de R$ {mensal:,.2f})")
                    else:
                        st.caption("Valor cadastrado")
                with c3:
                    st.markdown(f"**R$ {mensal:,.2f}/mês**")
                    st.caption("Custo mensal")
                with c_menu:
                    with st.popover("⋮"):
                        label_toggle = "❌ Desativar" if ativo else "✅ Ativar"
                        if st.button(label_toggle, key=f"toggle_desp_{row_id}", width="stretch"):
                            dm.toggle_despesa(row_id)
                            st.rerun()
                        if st.button("✏️ Editar", key=f"edit_desp_{row_id}", width="stretch"):
                            st.session_state[f"editing_desp_{row_id}"] = True
                            st.rerun()
                        # Botão para avançar parcela
                        if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")):
                            pagas = int(row["parcelas_pagas"]) if pd.notna(row.get("parcelas_pagas")) else 0
                            total_p = int(row["parcelas_total"])
                            if pagas < total_p:
                                if st.button("✓ Pagar parcela", key=f"pay_desp_{row_id}", width="stretch"):
                                    dm.update_despesa(row_id, parcelas_pagas=pagas + 1)
                                    if pagas + 1 >= total_p:
                                        dm.update_despesa(row_id, ativo=False)
                                    st.rerun()
                        if st.button("🗑️ Excluir", key=f"del_desp_{row_id}", width="stretch"):
                            st.session_state[f"confirm_del_desp_{row_id}"] = True
                            st.rerun()

                if st.session_state.get(f"confirm_del_desp_{row_id}", False):
                    st.warning(f"Confirma exclusão de '{row['descricao']}'?")
                    cc1, cc2, _ = st.columns([1, 1, 4])
                    with cc1:
                        if st.button("Sim, excluir", key=f"yes_del_desp_{row_id}", width="stretch"):
                            dm.delete_despesa(row_id)
                            del st.session_state[f"confirm_del_desp_{row_id}"]
                            st.rerun()
                    with cc2:
                        if st.button("Cancelar", key=f"no_del_desp_{row_id}", width="stretch"):
                            del st.session_state[f"confirm_del_desp_{row_id}"]
                            st.rerun()

                # Formulário de edição inline
                if st.session_state.get(f"editing_desp_{row_id}", False):
                    all_freqs = list(dm.FREQUENCIAS.keys()) + ["Parcelado"]
                    with st.form(f"form_edit_desp_{row_id}"):
                        st.markdown("**Editando registro**")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            edit_desc = st.text_input("Descrição", value=row["descricao"], key=f"ed_desc_d_{row_id}")
                            edit_valor = st.number_input("Valor (R$)", min_value=0.01, value=float(row["valor"]),
                                                          step=50.0, format="%.2f", key=f"ed_val_d_{row_id}")
                            edit_freq = st.selectbox("Frequência", all_freqs,
                                                      index=all_freqs.index(row["frequencia"])
                                                      if row["frequencia"] in all_freqs else 0,
                                                      key=f"ed_freq_d_{row_id}")
                            edit_venc = st.number_input("Dia do vencimento", min_value=0, max_value=31,
                                                         value=int(row["dia_vencimento"]) if pd.notna(row.get("dia_vencimento")) else 0,
                                                         key=f"ed_venc_d_{row_id}")
                        with ec2:
                            cat_index = categorias_despesa.index(row["categoria"]) if row["categoria"] in categorias_despesa else 0
                            edit_cat = st.selectbox("Categoria", categorias_despesa, index=cat_index,
                                                     key=f"ed_cat_d_{row_id}")
                            edit_dest = st.text_input("Destinatário",
                                                       value=str(row["destinatario"]) if pd.notna(row.get("destinatario")) else "",
                                                       key=f"ed_dest_d_{row_id}")
                            try:
                                dt_val = datetime.strptime(row["data_inicio"], "%Y-%m-%d").date()
                            except (ValueError, TypeError):
                                dt_val = date.today()
                            edit_data = st.date_input("Data de início", value=dt_val, key=f"ed_data_d_{row_id}")

                        st.markdown("##### Parcelamento")
                        ep1, ep2 = st.columns(2)
                        with ep1:
                            edit_parc_total = st.number_input("Total de parcelas", min_value=0,
                                                               value=int(row["parcelas_total"]) if pd.notna(row.get("parcelas_total")) else 0,
                                                               key=f"ed_pt_d_{row_id}")
                        with ep2:
                            edit_parc_pagas = st.number_input("Parcelas pagas", min_value=0,
                                                               value=int(row["parcelas_pagas"]) if pd.notna(row.get("parcelas_pagas")) else 0,
                                                               key=f"ed_pp_d_{row_id}")

                        bc1, bc2 = st.columns(2)
                        with bc1:
                            if st.form_submit_button("💾 Salvar", width="stretch", type="primary"):
                                dm.update_despesa(row_id,
                                                   descricao=edit_desc, valor=edit_valor,
                                                   frequencia=edit_freq, categoria=edit_cat,
                                                   destinatario=edit_dest.strip(),
                                                   data_inicio=edit_data.isoformat(),
                                                   dia_vencimento=edit_venc if edit_venc > 0 else pd.NA,
                                                   parcelas_total=edit_parc_total if edit_parc_total > 0 else pd.NA,
                                                   parcelas_pagas=edit_parc_pagas if edit_parc_total > 0 else pd.NA)
                                del st.session_state[f"editing_desp_{row_id}"]
                                st.rerun()
                        with bc2:
                            if st.form_submit_button("Cancelar", width="stretch"):
                                del st.session_state[f"editing_desp_{row_id}"]
                                st.rerun()

                st.markdown("---")
