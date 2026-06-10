import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Embarque Controlado",
    layout="wide"
)

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp{
    background: linear-gradient(135deg,#0f172a,#1e293b);
}

h1,h2,h3{
    color:white !important;
}

[data-testid="stMetric"]{
    background:#1E293B;
    border:1px solid #334155;
    padding:18px;
    border-radius:16px;
    box-shadow:0 4px 15px rgba(0,0,0,0.30);
}

[data-testid="stMetricValue"]{
    color:white;
    font-size:30px;
}

[data-testid="stMetricLabel"]{
    color:#CBD5E1;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TÍTULO
# =========================
st.markdown("""
<h1 style='text-align:center;color:white;'>
🚚 Embarque Controlado
</h1>

<p style='text-align:center;color:#94A3B8;font-size:18px;'>
Monitoramento de Qualidade • Retrabalho • Rastreabilidade
</p>
""", unsafe_allow_html=True)

# =========================
# DADOS (FAKE PARA FUNCIONAR)
# =========================
df = pd.DataFrame({
    "HORAS RETRABALHO": [1, 2, 3, 1, 4, 2],
    "NÚMERO DE SÉRIE": ["A1", "A2", "A3", "A4", "A5", "A6"],
    "MOTIVO DO ERRO": ["Falha", "Ajuste", "Erro", "Falha", "Erro", "Ajuste"],
    "SETOR CAUSADOR": ["Corte", "Montagem", "Pintura", "Montagem", "Corte", "Pintura"]
})

# =========================
# KPIs
# =========================
total_horas = df["HORAS RETRABALHO"].sum()
total_registros = len(df)
total_maquinas = df["NÚMERO DE SÉRIE"].nunique()
total_erros = df["MOTIVO DO ERRO"].count()

c1, c2, c3, c4 = st.columns(4)

c1.metric("⏱ Horas Retrabalho", f"{total_horas:.2f}")
c2.metric("📊 Registros", total_registros)
c3.metric("🔍 Máquinas", total_maquinas)
c4.metric("❌ Erros", total_erros)

# =========================
# QUALIDADE
# =========================
qualidade = max(0, 100 - ((total_erros / total_registros) * 100))

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=qualidade,
    title={"text": "Índice de Qualidade (%)"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "#10B981"},
        "steps": [
            {"range": [0, 60], "color": "#DC2626"},
            {"range": [60, 80], "color": "#F59E0B"},
            {"range": [80, 100], "color": "#10B981"}
        ]
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# =========================
# PARETO
# =========================
colA, colB = st.columns(2)

with colA:
    st.subheader("🎯 Pareto de Motivo do Erro")

    pareto = df.groupby("MOTIVO DO ERRO")["HORAS RETRABALHO"].sum().reset_index()

    fig = px.bar(
        pareto,
        y="MOTIVO DO ERRO",
        x="HORAS RETRABALHO",
        orientation="h",
        color="HORAS RETRABALHO",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        paper_bgcolor="#1E293B",
        plot_bgcolor="#1E293B",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# IA SCORE
# =========================
with colB:
    st.subheader("🧠 Ranking Inteligente")

    freq = df["MOTIVO DO ERRO"].value_counts()

    defeitos = df.groupby("MOTIVO DO ERRO").agg({
        "HORAS RETRABALHO": "sum"
    }).reset_index()

    defeitos["FREQUENCIA"] = defeitos["MOTIVO DO ERRO"].map(freq)

    defeitos["SCORE IA"] = defeitos["HORAS RETRABALHO"] * np.log1p(defeitos["FREQUENCIA"])

    defeitos = defeitos.sort_values("SCORE IA", ascending=False)

    fig2 = px.bar(
        defeitos,
        y="MOTIVO DO ERRO",
        x="SCORE IA",
        orientation="h",
        color="SCORE IA",
        color_continuous_scale="Blues"
    )

    fig2.update_layout(
        paper_bgcolor="#1E293B",
        plot_bgcolor="#1E293B",
        font_color="white"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# TABELA FINAL
# =========================
st.subheader("📋 Dados MES")
st.dataframe(df, use_container_width=True)
