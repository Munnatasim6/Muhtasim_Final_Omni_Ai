import streamlit as st
import pandas as pd
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import settings

st.set_page_config(page_title="OmniTrade AI Core", layout="wide", page_icon="⚡")

st.title("⚡ OmniTrade AI Core - God Mode")

# Sidebar
st.sidebar.header("System Status")
st.sidebar.success("System Online")
st.sidebar.info(f"Environment: {settings.ENV}")

import requests

# API Configuration
API_URL = "http://localhost:8000"

def fetch_api_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
    return None

# Tabs
tab1, tab2, tab3 = st.tabs(["Live Market", "Strategy Performance", "XAI Brain"])

# Fetch Data
sentiment_data = fetch_api_data("/market/sentiment")
agents_data = fetch_api_data("/status/agents")

with tab1:
    st.header("Live Market Data")
    col1, col2, col3 = st.columns(3)
    
    # Mock Price Data (since API doesn't expose price yet, or we could add it)
    # For now we keep static price but use real sentiment
    col1.metric("BTC/USDT", "$98,450.00", "+1.2%")
    
    if sentiment_data:
        score = sentiment_data.get('score', 0)
        label = sentiment_data.get('label', 'NEUTRAL')
        col2.metric("Market Sentiment", f"{score:.2f}", label)
        col3.metric("Interest Rate", f"{sentiment_data.get('interest_rate', 0)}%", "Fed")
    else:
        col2.metric("Market Sentiment", "Offline", "0.0")
        col3.metric("Interest Rate", "Offline", "0.0")
    
    st.subheader("Order Book Heatmap")
    st.image("https://placehold.co/800x400?text=Order+Book+Heatmap", caption="Real-time Liquidity")

with tab2:
    st.header("Strategy Performance")
    
    if agents_data:
        # Convert agents list to DataFrame
        df_agents = pd.DataFrame(agents_data)
        st.dataframe(df_agents)
        
        # Aggregate PnL
        total_pnl = df_agents['pnl'].sum() if 'pnl' in df_agents.columns else 0
        st.metric("Total Network PnL", f"${total_pnl:,.2f}")
    else:
        st.warning("No Agent Data Available")
        
    st.line_chart({"PnL": [0, 100, 120, 90, 150, 200, 180, 250]}) # Keep historical chart for now

with tab3:
    st.header("Explainable AI (XAI)")
    st.info("Why did the AI buy BTC?")
    
    # In a real app, we would fetch the latest trade decision explanation
    st.json({
        "Decision": "BUY",
        "Confidence": "92%",
        "Factors": {
            "RSI": "Oversold (28.5)",
            "Whale Alert": "Inflow > 500 BTC",
            "Sentiment": sentiment_data.get('label', 'UNKNOWN') if sentiment_data else "UNKNOWN"
        }
    })
    st.subheader("SHAP Values")
    st.bar_chart({"RSI": 0.4, "Volume": 0.3, "Sentiment": 0.2, "MACD": 0.1})
