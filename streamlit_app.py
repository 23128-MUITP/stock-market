import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os
import streamlit as st
from jugaad_data.nse import stock_df


df = None
def get_data(instr, ma):
    df = stock_df(symbol=instr, from_date=date(2024, 5, 5),
                  to_date=date(2025, 5, 5), series="EQ")
    df["MA_20"] = df["CLOSE"].rolling(window=ma).mean()
    df["DAILY_PCT_CHANGE"] = df["CLOSE"].pct_change() * 100
    df["DAILY_PCT_CHANGE"] = df["DAILY_PCT_CHANGE"].round(2)



def plot_saved_stock_data():

    df.sort_values('DATE', inplace=True)
    symbol = df['SYMBOL'].iloc[0] if 'SYMBOL' in df.columns else "Stock"

    plt.style.use("seaborn-darkgrid")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    fig.suptitle(f"{symbol} Price & Moving Average with Daily % Change", fontsize=16, fontweight='bold')

    ax1.plot(df['DATE'], df['CLOSE'], label='Close Price', color='dodgerblue', linewidth=2)
    ax1.plot(df['DATE'], df['MA_20'], label='20-Day MA', color='orange', linestyle='--', linewidth=2)
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    ax2.bar(df['DATE'], df['DAILY_PCT_CHANGE'],
            color=df['DAILY_PCT_CHANGE'].apply(lambda x: 'green' if x >= 0 else 'red'),
            width=1.0)
    ax2.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax2.set_ylabel('Daily % Change')
    ax2.set_xlabel('Date')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig)
    os.remove("DATA.csv")


# ==== Streamlit App ====

st.title("📈 Stock Price & MA Viewer")

symbol = st.text_input("Enter the name of the stock (ALL CAPS):", value="RELIANCE")
ma = st.number_input("Enter the length of moving average:", min_value=1, max_value=100, value=20)

if st.button("Generate Chart"):
    get_data(symbol, ma)
    plot_saved_stock_data("DATA.csv")
