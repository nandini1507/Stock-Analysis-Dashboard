import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------
# Title
# ------------------------------------
st.title("📈 Stock Analysis Dashboard")

# ------------------------------------
# User Input
# ------------------------------------
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, INFY)", "AAPL")

if st.button("Fetch Data"):
    # Fetch data
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")

    if df.empty:
        st.error("❌ Invalid ticker or no data found.")
    else:
        st.success(f"Data loaded for {ticker}")

        # ------------------------------------
        # Indicators
        # ------------------------------------
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

        # RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        RS = gain / loss
        df['RSI'] = 100 - (100 / (1 + RS))

        # ------------------------------------
        # Candlestick Chart
        # ------------------------------------
        st.subheader("📌 Candlestick Chart")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name="Candlestick"
        ))
        st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------
        # SMA / EMA Line Chart
        # ------------------------------------
        st.subheader("📌 Price with SMA & EMA")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df.index, y=df['Close'], mode="lines", name="Close"))
        fig2.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode="lines", name="SMA 20"))
        fig2.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], mode="lines", name="EMA 20"))
        st.plotly_chart(fig2, use_container_width=True)

        # ------------------------------------
        # RSI Chart
        # ------------------------------------
        st.subheader("📌 Relative Strength Index (RSI)")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode="lines", name="RSI"))
        fig3.add_hline(y=70, line_dash="dash", annotation_text="Overbought")
        fig3.add_hline(y=30, line_dash="dash", annotation_text="Oversold")
        st.plotly_chart(fig3, use_container_width=True)

        # ------------------------------------
        # Performance Summary
        # ------------------------------------
        st.subheader("📊 Performance Summary")
        first_close = df['Close'].iloc[0]
        last_close = df['Close'].iloc[-1]
        change = ((last_close - first_close) / first_close) * 100

        st.write(f"**Start Price:** {round(first_close, 2)}")
        st.write(f"**End Price:** {round(last_close, 2)}")
        st.write(f"📈 **Total Return:** {round(change, 2)} %")

        # ------------------------------------
        # CSV Download
        # ------------------------------------
        st.subheader("📥 Download Data")
        csv = df.to_csv().encode()
        st.download_button("Download CSV", csv, file_name=f"{ticker}_data.csv")
