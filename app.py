import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Embarque Controlado", layout="wide")

# =========================
# GOOGLE SHEETS CONNECTION (CORRETO)
# =========================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# JSON da credencial via secrets do Streamlit
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

client = gspread.authorize(creds)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1YfWO4Oa9fXF_bS7PS2NgRPUs1mrH8FIU8_kY4ANtkyI/edit"

sheet = client.open_by_url(SPREADSHEET_URL).sheet1

data = sheet.get_all_records()
df = pd.DataFrame(data)

# =========================
# LIMPEZA
# =========================
df.columns = df.columns.str.strip().str.upper()

if "HORAS RETRABALHO" not in df.columns:
    df["HORAS RETRABALHO"] = 0

df["HORAS RETRABALHO"] = pd.to_numeric(df["HORAS RETRABALHO"], errors="coerce").fillna(0)

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

st.success("Dashboard carregado com sucesso 🚀")
st.dataframe(df)