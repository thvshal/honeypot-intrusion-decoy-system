import streamlit as st
import pandas as pd

st.set_page_config(page_title="Threat Intel Dashboard", layout="wide")

st.title("🛡️ Autonomous Honeypot & Threat Intelligence Dashboard")
st.markdown("Real-time telemetry and LLM-driven intruder interaction tracking.")

LOG_FILE = "attack_logs.csv"

def load_data():
    try:
        df = pd.read_csv(LOG_FILE)
        return df
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Attacker_IP", "Command", "AI_Response"])

df = load_data()

# Top Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Total Intrusion Attempts", len(df))
col2.metric("Unique Attacker IPs", df["Attacker_IP"].nunique() if not df.empty else 0)
col3.metric("System Status", "ACTIVE & MONITORING", delta="Secure")

st.divider()

# Log Table
st.subheader("🚨 Live Attacker Telemetry Log")
if not df.empty:
    st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
else:
    st.info("No intrusions recorded yet. Start the honeypot server to begin capturing data.")

if st.button("Refresh Telemetry"):
    st.rerun()