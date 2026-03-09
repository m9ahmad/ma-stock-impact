import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIG (Must be the first command) ---
st.set_page_config(page_title="M&A Market Impact", layout="wide", page_icon="💹")

# --- 2. STYLING (Dark Theme for Financial Engineering) ---
st.html("""
<style>
    div[data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4B5563;
    }
    .main { background-color: #0e1117; }
</style>
""")

# --- 3. MAPPING & UTILS ---
TICKER_MAP = {
    "Google": "GOOGL",
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Facebook": "META",
    "IBM": "IBM",
    "Salesforce": "CRM",
    "Oracle": "ORCL"
}

# --- 4. DATA FETCHING (Corrected for yfinance MultiIndex Error) ---
@st.cache_data
def get_event_data(ticker, event_date):
    try:
        # Window: 30 days before, 90 days after
        start_dt = datetime.strptime(event_date, "%Y-%m-%d") - timedelta(days=30)
        end_dt = datetime.strptime(event_date, "%Y-%m-%d") + timedelta(days=90)
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        # Pulling both Ticker and S&P 500 at once to ensure date alignment
        raw_data = yf.download([ticker, '^GSPC'], start=start_str, end=end_str, progress=False)
        
        # FIX: Handle MultiIndex Columns gracefully
        if 'Adj Close' in raw_data.columns:
            data_filtered = raw_data['Adj Close']
        else:
            data_filtered = raw_data['Close']
            
        # Build clean DataFrame
        df = pd.DataFrame({
            'Stock': data_filtered[ticker],
            'Market': data_filtered['^GSPC']
        }).dropna()
        
        # Calculate Returns relative to the very first day in the window
        # This shows "Growth of $1" over the 120-day period
        df['Stock_Ret'] = (df['Stock'] / df['Stock'].iloc[0]) - 1
        df['Market_Ret'] = (df['Market'] / df['Market'].iloc[0]) - 1
        df['Alpha'] = df['Stock_Ret'] - df['Market_Ret']
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# --- 5. APP UI ---
st.title("💹 Event Study: Stock Impact of M&A")
st.caption("Analyzing market efficiency and shareholder value creation post-announcement.")

with st.sidebar:
    st.header("🏢 Strategy Selection")
    parent_name = st.selectbox("Select Acquirer", list(TICKER_MAP.keys()))
    # Examples of major deals
    st.info("💡 Try these dates:\n- 2016-06-13 (LinkedIn/MSFT)\n- 2020-12-01 (Slack/CRM)\n- 2018-06-04 (GitHub/MSFT)")
    event_date_input = st.text_input("Deal Date (YYYY-MM-DD)", "2016-06-13")

# --- 6. EXECUTION & VISUALS ---
ticker_sym = TICKER_MAP[parent_name]
analysis_df = get_event_data(ticker_sym, event_date_input)

if not analysis_df.empty:
    # KPI metrics for the window
    m1, m2, m3 = st.columns(3)
    
    total_stock_ret = analysis_df['Stock_Ret'].iloc[-1] * 100
    total_mkt_ret = analysis_df['Market_Ret'].iloc[-1] * 100
    final_alpha = analysis_df['Alpha'].iloc[-1] * 100
    
    m1.metric("Stock Performance", f"{total_stock_ret:.2f}%")
    m2.metric("S&P 500 Benchmark", f"{total_mkt_ret:.2f}%")
    m3.metric("Alpha (Excess Return)", f"{final_alpha:.2f}%", delta=f"{final_alpha:.1f}%")

    st.divider()

    # Plotting the "Alpha" Curve
    fig = go.Figure()
    
    # Stock Trace
    fig.add_trace(go.Scatter(
        x=analysis_df.index, 
        y=analysis_df['Stock_Ret'] * 100, 
        name=f"{ticker_sym} Return", 
        line=dict(color='#00ff88', width=3)
    ))
    
    # Market Trace
    fig.add_trace(go.Scatter(
        x=analysis_df.index, 
        y=analysis_df['Market_Ret'] * 100, 
        name="S&P 500 (Market)", 
        line=dict(color='#ff3366', dash='dash')
    ))
    
    # Event Marker (Day 0)
    event_dt_marker = datetime.strptime(event_date_input, "%Y-%m-%d")
    fig.add_vline(x=event_dt_marker, line_width=2, line_dash="dot", line_color="white")
    fig.add_annotation(x=event_dt_marker, y=0, text="Deal Announcement", showarrow=True, arrowhead=1)

    fig.update_layout(
        title=f"90-Day Market Reaction: {parent_name} Acquisition Impact",
        xaxis_title="Timeline",
        yaxis_title="Cumulative Return (%)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"**Analysis Conclusion:** In the 90 days following the announcement, **{parent_name}** {'outperformed' if final_alpha > 0 else 'underperformed'} the S&P 500 by **{abs(final_alpha):.2f}%**.")

else:
    st.warning("⚠️ Enter a valid historical date or check the sidebar for examples.")
