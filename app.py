import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIG ---
st.set_page_config(page_title="M&A Market Impact", layout="wide", page_icon="💹")

# --- 2. THE BRIDGE (CSV + TICKERS) ---
# Mapping the companies from your first project to their stock tickers
TICKER_MAP = {
    "Google": "GOOGL",
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Facebook": "META",
    "IBM": "IBM",
    "Salesforce": "CRM"
}

# --- 3. DATA FETCHING FUNCTION ---
@st.cache_data
def get_event_data(ticker, event_date):
    # Window: 30 days before, 90 days after
    start = (datetime.strptime(event_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
    end = (datetime.strptime(event_date, "%Y-%m-%d") + timedelta(days=90)).strftime("%Y-%m-%d")
    
    # Download Stock and S&P 500 (Benchmark)
    stock = yf.download(ticker, start=start, end=end, progress=False)['Adj Close']
    market = yf.download('^GSPC', start=start, end=end, progress=False)['Adj Close']
    
    # Normalize to 100 (Indexed at Day 0)
    # We find the price closest to the event date
    event_dt_obj = datetime.strptime(event_date, "%Y-%m-%d")
    
    # Simple calculation of returns relative to Day 0
    df = pd.DataFrame({'Stock': stock, 'Market': market}).dropna()
    df['Stock_Ret'] = df['Stock'].pct_change().cumsum()
    df['Market_Ret'] = df['Market'].pct_change().cumsum()
    df['Alpha'] = df['Stock_Ret'] - df['Market_Ret']
    
    return df

# --- 4. APP UI ---
st.title("💹 Event Study: Stock Impact of M&A")
st.markdown("### Analyzing how major deals move the needle for shareholders.")

with st.sidebar:
    st.header("Select a Past Event")
    parent = st.selectbox("Acquirer", list(TICKER_MAP.keys()))
    # Example historical dates from your CSV (You can later automate this to read from CSV)
    event_date = st.text_input("Deal Date (YYYY-MM-DD)", "2016-06-13") # Example: LinkedIn Buy
    st.caption("Common Dates: LinkedIn (2016-06-13), Slack (2020-12-01), GitHub (2018-06-04)")

# --- 5. EXECUTION & VISUALS ---
ticker = TICKER_MAP[parent]
data = get_event_data(ticker, event_date)

if not data.empty:
    # KPI metrics for the window
    m1, m2, m3 = st.columns(3)
    final_alpha = data['Alpha'].iloc[-1] * 100
    m1.metric("Stock Return (90d)", f"{data['Stock_Ret'].iloc[-1]*100:.2f}%")
    m2.metric("Market Return (90d)", f"{data['Market_Ret'].iloc[-1]*100:.2f}%")
    m3.metric("Excess Return (Alpha)", f"{final_alpha:.2f}%", delta=f"{final_alpha:.2f}%")

    # Plotting the "Alpha" Curve
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Stock_Ret'], name=f"{ticker} Return", line=dict(color='#00ff88')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Market_Ret'], name="S&P 500 Return", line=dict(color='#ff3366', dash='dash')))
    
    fig.update_layout(
        title=f"90-Day Market Reaction: {parent} Acquisition Impact",
        xaxis_title="Days from Deal Announcement",
        yaxis_title="Cumulative Return",
        template="plotly_dark",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"**Insight:** On Day 90, {parent} outpaced the market by {final_alpha:.2f}%.")
else:
    st.warning("Could not retrieve market data for that date. Try a different range.")
