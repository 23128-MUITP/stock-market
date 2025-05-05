import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from datetime import date
import os
import streamlit as st
from jugaad_data.nse import stock_df

# Required for Streamlit's hosted environments
os.environ["JUGAAD_DATA_DIR"] = "/tmp/jugaad_data_cache"

# Load symbol data
@st.cache_data
def load_symbol_data():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    df = df[["SYMBOL", "NAME OF COMPANY"]]
    df["DISPLAY"] = df["NAME OF COMPANY"].str.title() + " (" + df["SYMBOL"] + ")"
    df.sort_values("DISPLAY", inplace=True)
    return df

symbol_df = load_symbol_data()

# Fetch stock data
def get_data(instr, ma):
    df = stock_df(symbol=instr, from_date=date(2024, 5, 5),
                  to_date=date(2025, 5, 5), series="EQ")
    df["MA_20"] = df["CLOSE"].rolling(window=ma).mean()
    df["DAILY_PCT_CHANGE"] = df["CLOSE"].pct_change() * 100
    df["DAILY_PCT_CHANGE"] = df["DAILY_PCT_CHANGE"].round(2)
    return df

# Plot interactive chart
def plot_interactive(df, symbol, fullscreen=False):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df["DATE"], y=df["CLOSE"],
                             mode='lines', name='Close Price',
                             line=dict(color='dodgerblue')))
    
    fig.add_trace(go.Scatter(x=df["DATE"], y=df["MA_20"],
                             mode='lines', name='20-Day MA',
                             line=dict(color='orange', dash='dash')))

    fig.add_trace(go.Bar(x=df["DATE"], y=df["DAILY_PCT_CHANGE"],
                         name='Daily % Change',
                         marker_color=['green' if x >= 0 else 'red' for x in df["DAILY_PCT_CHANGE"]],
                         yaxis='y2', opacity=0.5))

    fig.update_layout(
        title=f"{symbol} Price & Moving Average with Daily % Change",
        xaxis_title="Date",
        yaxis=dict(title='Close Price / MA'),
        yaxis2=dict(title='Daily % Change', overlaying='y', side='right', showgrid=False),
        legend=dict(x=0, y=1),
        height=800 if fullscreen else 600,
        template='plotly_white',
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

# ==== Streamlit App ====
st.set_page_config(layout="wide")

st.title("📈 Stock Price & MA Viewer")

# Symbol selection with placeholder
company_list = ["Select Company"] + symbol_df["DISPLAY"].tolist()
selected_display = st.selectbox("Search for a stock (by name or symbol):", company_list)

if selected_display != "Select Company":
    symbol = symbol_df[symbol_df["DISPLAY"] == selected_display]["SYMBOL"].values[0]

    ma = st.number_input("Enter the length of moving average:", min_value=1, max_value=100, value=20)
    fullscreen = st.toggle("🖥️ Fullscreen Chart")

    if st.button("Generate Chart"):
        df = get_data(symbol, ma)
        df.sort_values('DATE', inplace=True)
        
        plot_interactive(df, symbol, fullscreen)

        with st.expander("📋 View Raw Data"):
            st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"{symbol}_data.csv",
            mime='text/csv'
        )
else:
    st.info("Please select a company to continue.")
