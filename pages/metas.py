"""Página de Metas Financeiras."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import data_manager as dm
from datetime import date, datetime

st.title("🎯 Metas Financeiras")
st.markdown("---")

# Formulário de nova meta
with st.expander("➕ Adicionar Nova Meta", expanded=False):
    with st.form("form_meta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descrição *", placeholder="Ex: Reserva de emergência")
            valor_alvo = st.number_input("Valor alvo (R$) *", min_value=0.01, step=500.0, format="%.2f")
            categoria = st.selectbox("Categoria", [
                "Reserva de Emergência",
                "Viagem",
                "Veículo",
                "Imóvel",
                "Educação",
                "Aposentadoria",
                "Investimento",
                "Outro",
            ])
        with col2:
            valor_atual = st.number_input("Valor atual (R$)", min_value=0.0, step=100.0, format="%.2f")
            data_limite = st.date_input("Data limite", value=date(date.today().year + 1, 12, 31))

        submitted = st.form_submit_button("Salvar Meta", width="stretch", type="primary")
        if submitted:
            if not descricao.strip():
                st.error("Preencha a descrição.")
            else:
                dm.add_meta(descricao, valor_alvo, valor_atual, data_limite.isoformat(), categoria)
                st.success(f"Meta '{descricao}' cadastrada!")
                st.rerun()

# Lista de metas
metas_df = dm.load_metas()

if metas_df.empty:
    st.info("Nenhuma meta cadastrada. Use o formulário acima para adicionar.")
else:
    ativas = metas_df[metas_df["ativo"] == True]
    concluidas = metas_df[(metas_df["ativo"] == True) & (metas_df["valor_atual"] >= metas_df["valor_alvo"])]

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Metas Ativas", len(ativas))
    with col_m2:
        st.metric("Metas Concluídas", len(concluidas))
    with col_m3:
        total_falta = (ativas["valor_alvo"] - ativas["valor_atual"]).clip(lower=0).sum()
        st.metric("Total Restante", f"R$ {total_falta:,.2f}")

    st.markdown("---")

    for _, row in metas_df.iterrows():
        row_id = int(row["id"])
        progresso = min(row["valor_atual"] / row["valor_alvo"], 1.0) if row["valor_alvo"] > 0 else 0
        falta = max(row["valor_alvo"] - row["valor_atual"], 0)

        # Calcular meses restantes
        try:
            data_lim = datetime.strptime(row["data_limite"], "%Y-%m-%d").date()
            dias_restantes = (data_lim - date.today()).days
            meses_restantes = max(dias_restantes / 30, 1)
            valor_mensal_necessario = falta / meses_restantes if falta > 0 else 0
        except (ValueError, TypeError):
            dias_restantes = 0
            meses_restantes = 0
            valor_mensal_necessario = 0

        status = "✅ Concluída!" if progresso >= 1 else ("⛔ Inativa" if not row["ativo"] else "🔵 Em andamento")

        with st.container():
            st.markdown(f"### {status} {row['descricao']}")
            st.caption(f"{row['categoria']} • Limite: {row['data_limite']}")

            st.progress(progresso, text=f"{progresso*100:.1f}% — R$ {row['valor_atual']:,.2f} / R$ {row['valor_alvo']:,.2f}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Faltam", f"R$ {falta:,.2f}")
            with col2:
                if dias_restantes > 0:
                    st.metric("Dias Restantes", f"{dias_restantes}")
                else:
                    st.metric("Dias Restantes", "Prazo vencido" if progresso < 1 else "—")
            with col3:
                if valor_mensal_necessario > 0:
                    st.metric("Necessário/mês", f"R$ {valor_mensal_necessario:,.2f}")
                else:
                    st.metric("Necessário/mês", "—")
            with col4:
                saldo_mensal = dm.saldo_mensal()
                if valor_mensal_necessario > 0 and saldo_mensal > 0:
                    viavel = "✅ Viável" if saldo_mensal >= valor_mensal_necessario else "⚠️ Apertado"
                    st.metric("Viabilidade", viavel)
                else:
                    st.metric("Viabilidade", "—")

            # Ações
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            with col_a1:
                novo_valor = st.number_input(
                    "Atualizar valor atual (R$)",
                    min_value=0.0,
                    value=float(row["valor_atual"]),
                    step=100.0,
                    format="%.2f",
                    key=f"valor_meta_{row_id}",
                )
            with col_a2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Atualizar", key=f"update_meta_{row_id}", width="stretch"):
                    dm.update_meta(row_id, valor_atual=novo_valor)
                    st.rerun()
            with col_a3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_meta_{row_id}", width="stretch"):
                    st.session_state[f"confirm_del_meta_{row_id}"] = True

                if st.session_state.get(f"confirm_del_meta_{row_id}", False):
                    st.warning(f"Confirma exclusão de '{row['descricao']}'?")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("Sim", key=f"yes_del_meta_{row_id}", width="stretch"):
                            dm.delete_meta(row_id)
                            del st.session_state[f"confirm_del_meta_{row_id}"]
                            st.rerun()
                    with cc2:
                        if st.button("Não", key=f"no_del_meta_{row_id}", width="stretch"):
                            del st.session_state[f"confirm_del_meta_{row_id}"]
                            st.rerun()
            with col_a4:
                pass

            st.markdown("---")
