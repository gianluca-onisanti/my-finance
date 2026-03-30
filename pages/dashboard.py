"""Dashboard - Visão geral das finanças."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import data_manager as dm
import pandas as pd

st.title("📊 Dashboard")
st.markdown("---")

receitas_df = dm.load_receitas()
despesas_df = dm.load_despesas()

total_rec = dm.total_receitas_mensal(receitas_df)
total_desp = dm.total_despesas_mensal(despesas_df)
saldo = total_rec - total_desp
taxa_poup = dm.taxa_poupanca()

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Receita Mensal",
        value=f"R$ {total_rec:,.2f}",
    )

with col2:
    st.metric(
        label="Despesa Mensal",
        value=f"R$ {total_desp:,.2f}",
    )

with col3:
    st.metric(
        label="Saldo Mensal",
        value=f"R$ {saldo:,.2f}",
        delta=f"R$ {saldo:,.2f}",
        delta_color="normal" if saldo >= 0 else "inverse",
    )

with col4:
    st.metric(
        label="Taxa de Poupança",
        value=f"{taxa_poup:.1f}%",
        delta=f"{taxa_poup:.1f}%",
        delta_color="normal" if taxa_poup >= 0 else "inverse",
    )

st.markdown("---")

# Gráficos
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Despesas por Categoria")
    desp_cat = dm.despesas_por_categoria(despesas_df)
    if not desp_cat.empty:
        fig = px.pie(
            desp_cat,
            values="valor_mensal",
            names="categoria",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Nenhuma despesa cadastrada ainda.")

with col_right:
    st.subheader("Receitas por Categoria")
    rec_cat = dm.receitas_por_categoria(receitas_df)
    if not rec_cat.empty:
        fig = px.pie(
            rec_cat,
            values="valor_mensal",
            names="categoria",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Nenhuma receita cadastrada ainda.")

# Comparação Receitas vs Despesas
st.subheader("Receitas vs Despesas (Visão Mensal)")
if total_rec > 0 or total_desp > 0:
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=["Receitas", "Despesas", "Saldo"],
        y=[total_rec, total_desp, saldo],
        marker_color=["#4CAF50", "#f44336", "#2196F3" if saldo >= 0 else "#ff9800"],
        text=[f"R$ {total_rec:,.2f}", f"R$ {total_desp:,.2f}", f"R$ {saldo:,.2f}"],
        textposition="outside",
    ))
    fig_bar.update_layout(
        yaxis_title="Valor (R$)",
        showlegend=False,
        margin=dict(t=20, b=20),
        height=350,
    )
    st.plotly_chart(fig_bar, width="stretch")

# Repasses por Destinatário
st.subheader("Repasses por Destinatário")
desp_dest = dm.despesas_por_destinatario(despesas_df)
if not desp_dest.empty:
    fig_dest = px.bar(
        desp_dest,
        x="destinatario",
        y="valor_mensal",
        text=desp_dest["valor_mensal"].apply(lambda v: f"R$ {v:,.2f}"),
        color="destinatario",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_dest.update_layout(
        yaxis_title="Valor Mensal (R$)",
        xaxis_title="",
        showlegend=False,
        height=380,
        margin=dict(t=20, b=20),
    )
    fig_dest.update_traces(textposition="outside")
    st.plotly_chart(fig_dest, width="stretch")
else:
    st.info("Nenhuma despesa com destinatário cadastrado. Adicione destinatários nas despesas para ver os repasses.")

st.markdown("---")

# Projeção anual
st.subheader("Projeção Anual")
col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    st.metric("Receita Anual Projetada", f"R$ {total_rec * 12:,.2f}")
with col_a2:
    st.metric("Despesa Anual Projetada", f"R$ {total_desp * 12:,.2f}")
with col_a3:
    saldo_anual = saldo * 12
    st.metric("Economia Anual Projetada", f"R$ {saldo_anual:,.2f}",
              delta=f"R$ {saldo_anual:,.2f}",
              delta_color="normal" if saldo_anual >= 0 else "inverse")

# Próximos vencimentos
st.markdown("---")
st.subheader("Próximos Vencimentos")
despesas_ativas = despesas_df[despesas_df["ativo"] == True].copy()
despesas_com_venc = despesas_ativas[despesas_ativas["dia_vencimento"].notna()].copy()

if not despesas_com_venc.empty:
    despesas_com_venc = despesas_com_venc.sort_values("dia_vencimento")
    from datetime import datetime
    dia_hoje = datetime.now().day

    for _, row in despesas_com_venc.iterrows():
        dia = int(row["dia_vencimento"])
        status = "🔴 Vencido" if dia < dia_hoje else ("🟡 Hoje" if dia == dia_hoje else "🟢 A vencer")
        parcela_info = ""
        if row["frequencia"] == "Parcelado" and pd.notna(row.get("parcelas_total")):
            parcela_info = f" | Parcela {int(row['parcelas_pagas'])}/{int(row['parcelas_total'])}"
        st.markdown(f"**Dia {dia:02d}** - {row['descricao']} — R$ {row['valor']:,.2f} ({row['categoria']}){parcela_info} {status}")
else:
    st.info("Nenhuma despesa com dia de vencimento cadastrado.")
