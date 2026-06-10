import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Embarque Controlado",
    layout="wide"
)

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

st.markdown("""
<h1 style='text-align:center;color:white;'>
🚚 Embarque Controlado
</h1>

<p style='text-align:center;color:#94A3B8;font-size:18px;'>
Monitoramento de Qualidade • Retrabalho • Rastreabilidade
</p>
""", unsafe_allow_html=True)

url_planilha = "https://docs.google.com/spreadsheets/d/1YfWO4Oa9fXF_bS7PS2NgRPUs1mrH8FIU8_kY4ANtkyI/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        spreadsheet=url_planilha,
        ttl="5m"
    )

    # =========================
    # LIMPEZA
    # =========================
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace("Ç", "C")
    )

    if "HORAS RETRABALHO" not in df.columns:
        df["HORAS RETRABALHO"] = 0

    df["HORAS RETRABALHO"] = pd.to_numeric(
        df["HORAS RETRABALHO"],
        errors="coerce"
    ).fillna(0)

    # =========================
    # KPIs
    # =========================
    total_horas = df["HORAS RETRABALHO"].sum()
    total_registros = len(df)

    total_maquinas = df["NÚMERO DE SÉRIE"].nunique() if "NÚMERO DE SÉRIE" in df.columns else 0
    total_erros = df["MOTIVO DO ERRO"].count() if "MOTIVO DO ERRO" in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("⏱ Horas Retrabalho", f"{total_horas:.2f}")
    c2.metric("📊 Registros", total_registros)
    c3.metric("🔍 Máquinas", total_maquinas)
    c4.metric("❌ Erros", total_erros)

    qualidade = max(
        0,
        100 - ((total_erros / max(total_registros, 1)) * 100)
    )

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
    # GRÁFICOS
    # =========================
    colA, colB = st.columns(2)

    pareto = None
    defeitos = None

    with colA:
        st.subheader("🎯 Pareto de Motivo do Erro")

        if "MOTIVO DO ERRO" in df.columns:
            pareto = (
                df.groupby("MOTIVO DO ERRO")["HORAS RETRABALHO"]
                .sum()
                .reset_index()
                .sort_values(by="HORAS RETRABALHO", ascending=False)
            )

            fig = px.bar(
                pareto.head(10),
                y="MOTIVO DO ERRO",
                x="HORAS RETRABALHO",
                orientation="h",
                text="HORAS RETRABALHO",
                color="HORAS RETRABALHO",
                color_continuous_scale="Reds"
            )

            fig.update_traces(textposition="outside")

            fig.update_layout(
                height=500,
                paper_bgcolor="#1E293B",
                plot_bgcolor="#1E293B",
                font_color="white",
                yaxis_title="",
                xaxis_title="Horas de Retrabalho",
                coloraxis_showscale=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.subheader("🧠 Ranking Inteligente de Defeitos")

        if "MOTIVO DO ERRO" in df.columns:
            defeitos = (
                df.groupby("MOTIVO DO ERRO")
                .agg({"HORAS RETRABALHO": "sum"})
                .reset_index()
            )

            freq = df["MOTIVO DO ERRO"].value_counts()

            defeitos["FREQUENCIA"] = defeitos["MOTIVO DO ERRO"].map(freq)

            defeitos["SCORE IA"] = (
                defeitos["HORAS RETRABALHO"] * np.log1p(defeitos["FREQUENCIA"])
            )

            defeitos = defeitos.sort_values("SCORE IA", ascending=False)

            fig_ai = px.bar(
                defeitos.head(10),
                y="MOTIVO DO ERRO",
                x="SCORE IA",
                orientation="h",
                text="SCORE IA",
                color="SCORE IA",
                color_continuous_scale="Blues"
            )

            fig_ai.update_traces(textposition="outside")

            fig_ai.update_layout(
                height=500,
                paper_bgcolor="#1E293B",
                plot_bgcolor="#1E293B",
                font_color="white",
                yaxis_title="",
                xaxis_title="Score IA",
                coloraxis_showscale=False
            )

            st.plotly_chart(fig_ai, use_container_width=True)

    # =========================
    # SETOR
    # =========================
    st.subheader("🥧 Retrabalho por Setor")

    if "SETOR CAUSADOR" in df.columns:
        setor = (
            df.groupby("SETOR CAUSADOR")["HORAS RETRABALHO"]
            .sum()
            .reset_index()
        )

        fig_pizza = px.pie(
            setor,
            names="SETOR CAUSADOR",
            values="HORAS RETRABALHO",
            hole=0.70,
            color_discrete_sequence=px.colors.sequential.Teal
        )

        fig_pizza.update_traces(textposition="inside", textinfo="percent+label")
        fig_pizza.update_layout(paper_bgcolor="#1E293B", font_color="white")

        st.plotly_chart(fig_pizza, use_container_width=True)

        # =========================
        # HEATMAP
        # =========================
        st.subheader("🔥 Mapa de Calor - Setor x Defeito")

        heat = pd.crosstab(
            df["SETOR CAUSADOR"],
            df["MOTIVO DO ERRO"]
        )

        fig_heat = px.imshow(
            heat,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Reds"
        )

        fig_heat.update_layout(
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
            font_color="white"
        )

        st.plotly_chart(fig_heat, use_container_width=True)

        # =========================
        # TOP 3
        # =========================
        if defeitos is not None and len(defeitos) > 0:
            st.subheader("🚨 Top 3 Problemas Críticos")

            for _, row in defeitos.head(3).iterrows():
                st.warning(f"{row['MOTIVO DO ERRO']} | Score IA: {row['SCORE IA']:.2f}")

    # =========================
    # RASTREABILIDADE
    # =========================
    st.subheader("📦 Rastreabilidade por Número de Série")

    if "NÚMERO DE SÉRIE" in df.columns:
        serial = st.text_input("Digite o Número de Série")

        if serial:
            rastreio = df[
                df["NÚMERO DE SÉRIE"].astype(str).str.contains(serial, na=False)
            ]

            if rastreio.empty:
                st.warning("Nenhum registro encontrado.")
            else:
                st.success(f"{len(rastreio)} registros encontrados")

                r1, r2 = st.columns(2)

                r1.metric("Horas Retrabalho", f"{rastreio['HORAS RETRABALHO'].sum():.2f}")
                r2.metric("Ocorrências", len(rastreio))

                st.dataframe(rastreio, use_container_width=True)

    # =========================
    # TABELA FINAL
    # =========================
    st.subheader("📋 Dados MES")

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Erro no sistema MES")
    st.code(str(e))