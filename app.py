import streamlit as st
import pandas as pd
import yfinance as yf
usdthb = yf.download("THB=X", period="1d")["Close"].iloc[-1]
st.set_page_config(layout="wide")

st.title("🇹🇭 Advanced Hyperinflation Dashboard (Thailand)")

# ===== DATA =====
@st.cache_data
def load_data():
    usdthb = yf.download("THB=X", period="3mo")
    gold = yf.download("GC=F", period="3mo")
    oil = yf.download("CL=F", period="3mo")
    return usdthb, gold, oil

usdthb, gold, oil = load_data()

latest_usdthb = usdthb["Close"].iloc[-1]

# ===== SCORING =====
def currency_score(x):
    if x < 35: return 2
    elif x < 40: return 5
    elif x < 45: return 7
    else: return 9

currency = currency_score(latest_usdthb)


st.sidebar.header("Manual Inputs")

cpi = st.sidebar.slider("CPI (%)", 0.0, 50.0, 6.0)
policy = st.sidebar.selectbox("Policy", ["None", "Price Control", "Capital Control"])
behavior = st.sidebar.slider("Behavior Shift", 0, 10, 4)

def inflation_score(x):
    if x < 5: return 2
    elif x < 10: return 5
    elif x < 20: return 7
    else: return 9

def policy_score(x):
    if x == "None": return 2
    elif x == "Price Control": return 6
    else: return 10

inflation = inflation_score(cpi)
policy_s = policy_score(policy)

# ===== TOTAL SCORE =====
total_score = (
    currency * 0.30 +
    inflation * 0.20 +
    5 * 0.20 +   # placeholder financial
    policy_s * 0.15 +
    behavior * 0.15
)

# ===== PHASE =====
if total_score < 5:
    phase = "Phase 2"
elif total_score < 7:
    phase = "Late Phase 2"
elif total_score < 9:
    phase = "Transition"
else:
    phase = "Phase 3"

# ===== SIGNAL =====
if phase == "Phase 2":
    signal = "Normal Allocation"
    alloc = {"Equity":60,"Energy":20,"Gold":10,"Cash":10}
elif phase == "Late Phase 2":
    signal = "Increase Energy/Gold"
    alloc = {"Equity":40,"Energy":30,"Gold":20,"Cash":10}
elif phase == "Transition":
    signal = "Shift to USD"
    alloc = {"Equity":20,"Energy":25,"Gold":25,"Cash":30}
else:
    signal = "Capital Preservation"
    alloc = {"Equity":10,"Energy":20,"Gold":30,"Cash":40}

# ===== DISPLAY =====
col1, col2, col3 = st.columns(3)
col1.metric("USD/THB", round(latest_usdthb,2))
col2.metric("Score", round(total_score,2))
col3.metric("Phase", phase)

st.subheader("Signal")
st.warning(signal)

# ===== CHARTS =====
st.subheader("Market Data")
st.line_chart(usdthb["Close"])
st.line_chart(gold["Close"])
st.line_chart(oil["Close"])
st.line_chart(usdthb_history)
# ===== PORTFOLIO =====
st.subheader("Recommended Allocation")
st.bar_chart(pd.Series(alloc))

# ===== ALERT =====
if total_score > 7:
    st.error("🚨 ALERT: Entering Hyperinflation Transition")

# ===== SCENARIO =====
st.subheader("Scenario Simulation")

sim_usd = st.slider("Simulate USD/THB", 30.0, 60.0, float(latest_usdthb))

sim_currency = currency_score(sim_usd)
sim_total = (
    sim_currency * 0.30 +
    inflation * 0.20 +
    5 * 0.20 +
    policy_s * 0.15 +
    behavior * 0.15
)

st.write("Simulated Score:", round(sim_total,2))
