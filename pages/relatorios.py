"""Página de Relatórios e Análises."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import data_manager as dm

st.title("📈 Relatórios e Análises")
st.markdown("---")

receitas_df = dm.load_receitas()
despesas_df = dm.load_despesas()

total_rec = dm.total_receitas_mensal(receitas_df)
total_desp = dm.total_despesas_mensal(despesas_df)
saldo = total_rec - total_desp

# --- Análise detalhada por categoria ---
st.subheader("Análise Detalhada por Categoria de Despesa")

desp_cat = dm.despesas_por_categoria(despesas_df)
if not desp_cat.empty:
    desp_cat["percentual"] = (desp_cat["valor_mensal"] / desp_cat["valor_mensal"].sum() * 100).round(1)
    desp_cat["percentual_renda"] = (desp_cat["valor_mensal"] / total_rec * 100).round(1) if total_rec > 0 else 0

    fig = px.bar(
        desp_cat,
        x="categoria",
        y="valor_mensal",
        text=desp_cat.apply(lambda r: f"R$ {r['valor_mensal']:,.2f} ({r['percentual']}%)", axis=1),
        color="categoria",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_layout(
        yaxis_title="Valor Mensal (R$)",
        xaxis_title="",
        showlegend=False,
        height=400,
        margin=dict(t=20, b=20),
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, width="stretch")

    # Tabela detalhada
    tabela = desp_cat.copy()
    tabela.columns = ["Categoria", "Valor Mensal", "% do Total", "% da Renda"]
    tabela["Valor Mensal"] = tabela["Valor Mensal"].apply(lambda x: f"R$ {x:,.2f}")
    tabela["% do Total"] = tabela["% do Total"].apply(lambda x: f"{x}%")
    tabela["% da Renda"] = tabela["% da Renda"].apply(lambda x: f"{x}%")
    st.dataframe(tabela, width="stretch", hide_index=True)
else:
    st.info("Nenhuma despesa ativa para analisar.")

st.markdown("---")

# --- Regra 50/30/20 ---
st.subheader("Análise 50/30/20")
st.caption("Uma regra popular de orçamento: 50% para necessidades, 30% para desejos, 20% para poupança/investimentos.")

categorias_necessidades = {"Moradia", "Alimentação", "Transporte", "Saúde", "Seguros", "Impostos"}
categorias_desejos = {"Lazer", "Vestuário", "Assinaturas", "Presentes", "Pets"}
categorias_poupanca = {"Investimentos", "Dívidas"}

despesas_ativas = despesas_df[despesas_df["ativo"] == True].copy()

if not despesas_ativas.empty and total_rec > 0:
    despesas_ativas["valor_mensal"] = despesas_ativas.apply(
        lambda r: r["valor"] / r["parcelas_total"] if r["frequencia"] == "Parcelado" and pd.notna(r.get("parcelas_total")) and pd.notna(r.get("parcelas_pagas")) and r["parcelas_pagas"] < r["parcelas_total"]
        else dm.valor_mensal(r["valor"], r["frequencia"]),
        axis=1,
    )

    necessidades = despesas_ativas[despesas_ativas["categoria"].isin(categorias_necessidades)]["valor_mensal"].sum()
    desejos = despesas_ativas[despesas_ativas["categoria"].isin(categorias_desejos)]["valor_mensal"].sum()
    poupanca_desp = despesas_ativas[despesas_ativas["categoria"].isin(categorias_poupanca)]["valor_mensal"].sum()
    outros = total_desp - necessidades - desejos - poupanca_desp
    poupanca_real = saldo + poupanca_desp

    col1, col2, col3 = st.columns(3)

    with col1:
        pct_nec = (necessidades / total_rec * 100) if total_rec > 0 else 0
        st.metric("Necessidades", f"R$ {necessidades:,.2f}", f"{pct_nec:.1f}% (meta: 50%)")
        color = "🟢" if pct_nec <= 50 else "🔴"
        st.markdown(f"{color} {'Dentro' if pct_nec <= 50 else 'Acima'} do recomendado")

    with col2:
        pct_des = (desejos / total_rec * 100) if total_rec > 0 else 0
        st.metric("Desejos", f"R$ {desejos:,.2f}", f"{pct_des:.1f}% (meta: 30%)")
        color = "🟢" if pct_des <= 30 else "🔴"
        st.markdown(f"{color} {'Dentro' if pct_des <= 30 else 'Acima'} do recomendado")

    with col3:
        pct_poup = (poupanca_real / total_rec * 100) if total_rec > 0 else 0
        st.metric("Poupança/Investimentos", f"R$ {poupanca_real:,.2f}", f"{pct_poup:.1f}% (meta: 20%)")
        color = "🟢" if pct_poup >= 20 else "🔴"
        st.markdown(f"{color} {'Dentro' if pct_poup >= 20 else 'Abaixo'} do recomendado")

    # Gráfico comparativo
    fig_gauge = go.Figure(data=[
        go.Bar(name="Real", x=["Necessidades", "Desejos", "Poupança"], y=[pct_nec, pct_des, pct_poup],
               marker_color=["#FF6B6B", "#4ECDC4", "#45B7D1"],
               text=[f"{v:.1f}%" for v in [pct_nec, pct_des, pct_poup]], textposition="outside"),
        go.Bar(name="Meta", x=["Necessidades", "Desejos", "Poupança"], y=[50, 30, 20],
               marker_color=["rgba(0,0,0,0.15)"] * 3,
               text=["50%", "30%", "20%"], textposition="outside"),
    ])
    fig_gauge.update_layout(
        barmode="group",
        yaxis_title="% da Renda",
        height=350,
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_gauge, width="stretch")
else:
    st.info("Cadastre receitas e despesas para ver a análise 50/30/20.")

st.markdown("---")

# --- Gastos fixos vs variáveis ---
st.subheader("Despesas Fixas vs Variáveis")

if not despesas_ativas.empty:
    freq_fixas = {"Mensal", "Semanal", "Quinzenal"}
    freq_variaveis = { "Bimestral", "Trimestral", "Semestral", "Anual", "Pontual", "Parcelado"}

    fixas = despesas_ativas[despesas_ativas["frequencia"].isin(freq_fixas)]["valor_mensal"].sum()
    variaveis = despesas_ativas[despesas_ativas["frequencia"].isin(freq_variaveis)]["valor_mensal"].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Despesas Fixas", f"R$ {fixas:,.2f}", f"{(fixas/total_desp*100):.1f}% do total" if total_desp > 0 else "0%")
    with col2:
        st.metric("Despesas Variáveis / Esporádicas", f"R$ {variaveis:,.2f}", f"{(variaveis/total_desp*100):.1f}% do total" if total_desp > 0 else "0%")

    fig_fixo_var = px.pie(
        values=[fixas, variaveis],
        names=["Fixas", "Variáveis/Esporádicas"],
        hole=0.4,
        color_discrete_sequence=["#667eea", "#f093fb"],
    )
    fig_fixo_var.update_layout(margin=dict(t=20, b=20), height=300)
    st.plotly_chart(fig_fixo_var, width="stretch")

st.markdown("---")

# --- Comprometimento da renda ---
st.subheader("Comprometimento da Renda")

if total_rec > 0:
    comprometido = (total_desp / total_rec * 100)
    livre = 100 - comprometido

    fig_comp = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=comprometido,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "% da renda comprometida"},
        delta={"reference": 80, "decreasing": {"color": "green"}, "increasing": {"color": "red"}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#667eea"},
            "steps": [
                {"range": [0, 50], "color": "#E8F5E9"},
                {"range": [50, 80], "color": "#FFF9C4"},
                {"range": [80, 100], "color": "#FFCDD2"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 80,
            },
        },
    ))
    fig_comp.update_layout(height=350, margin=dict(t=60, b=20))
    st.plotly_chart(fig_comp, width="stretch")

    if comprometido <= 50:
        st.success("Excelente! Você tem bastante margem financeira.")
    elif comprometido <= 70:
        st.info("Bom! Sua renda está razoavelmente comprometida.")
    elif comprometido <= 80:
        st.warning("Atenção! Sua renda está significativamente comprometida.")
    else:
        st.error("Alerta! Sua renda está muito comprometida. Considere revisar seus gastos.")
