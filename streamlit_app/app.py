import subprocess
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path("data/trades.db")
TABLE = "trades"

st.set_page_config(page_title="Futures Liquidity Monitor", layout="wide")
st.title("Futures Liquidity Monitor")
st.caption("ETL → SQL analytics → Streamlit dashboard (synthetic trade data)")

def build_data():
    st.info("Building dataset for first run (generating data + running ETL)...")
    subprocess.run(["python", "generate_sample_data.py"], check=True)
    subprocess.run(["python", "etl/etl.py"], check=True)

if not DB_PATH.exists():
    try:
        build_data()
    except Exception as e:
        st.error(f"Failed to build data automatically: {e}")
        st.stop()

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM {TABLE}", conn, parse_dates=["timestamp", "minute"])
    conn.close()
    return df

df = load_data()

col1, col2 = st.columns(2)
col1.metric("Total Trades", f"{len(df):,}")
col2.metric("Total Volume", f"{int(df['size'].sum()):,}")

vol = df.groupby("instrument")["size"].sum().sort_values(ascending=False)
st.subheader("Volume by Instrument")
st.bar_chart(vol)

st.subheader("Sample Trades")
st.dataframe(df.head(200), use_container_width=True)
