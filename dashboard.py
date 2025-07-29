import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from prompt_tracker import prompt_tracking_dashboard

st.set_page_config(page_title="Red Machine", layout="wide")
    # Add security header to bypass web login
st.markdown(
    """
    <style>
        #hidden-title, .hidden-data-science-font, h2>span, li>span, .pandas-dataframe, .markdown-title, h3>span{
            visibility: hidden !important;
        }
    </style>
    """, unsafe_allow_html=True)
st.title("📊 SENSEX Options Trading Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Model Accuracy", "Live Trades", "Backtest", "Prompt Tracking"])

with tab1:
    # --- Model Accuracy Trend ---
    st.header("📈 Model Accuracy Over Time")
    try:
        log_df = pd.read_csv("model_log.txt", sep="|", header=None, names=["Timestamp", "Model Path", "Accuracy"])
        log_df['Accuracy'] = log_df['Accuracy'].str.extract(r"Accuracy: ([\d\.]+)").astype(float)
        log_df['Timestamp'] = pd.to_datetime(log_df['Timestamp'])
        fig1 = px.line(log_df, x="Timestamp", y="Accuracy", title="Model Accuracy Trend")
        st.plotly_chart(fig1, use_container_width=True)
    except FileNotFoundError:
        st.warning("model_log.txt not found. Run the trading model to generate logs.")

with tab2:
    # --- Trade Execution Summary ---
    st.header("📊 Live Trade Execution Summary")
    try:
        trades = pd.read_csv("trade_log.csv", header=0, parse_dates=['timestamp'])


        st.dataframe(trades.tail(50), use_container_width=True)

        # Display metrics for paper trades
        st.subheader("Paper Trade Metrics")
        paper_trades = trades[trades['mode'] == 'paper']
        total_paper_trades = len(paper_trades)
        successful_paper_trades = paper_trades[paper_trades['status'] == 'PAPER_EXECUTED'].shape[0]
        st.write(f"Total Paper Trades: {total_paper_trades}")
        st.write(f"Successful Paper Trades: {successful_paper_trades}")

        status_counts = trades['status'].value_counts().reset_index(name='Count')
        status_counts.columns = ['Status', 'Count']
        fig2 = px.pie(status_counts, names='Status', values='Count', title='Trade Execution Status Split')
        st.plotly_chart(fig2, use_container_width=True)
    except FileNotFoundError:
        st.warning("trade_log.csv not found. No live trade data available.")

with tab3:
    # --- Backtest Analytics ---
    st.header("🔍 Backtest Performance Analysis")
    try:
        backtest_df = pd.read_csv("backtest_results.csv")
        st.dataframe(backtest_df.head(), use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Trades", backtest_df[backtest_df['signal'] != 'HOLD'].shape[0])
        with col2:
            st.metric("Average PnL per Trade", f"{backtest_df['pnl'].mean():.2f}")
        with col3:
            st.metric("Hit Rate", f"{backtest_df['pnl'].gt(0).mean():.2%}")

        # PnL over time
        backtest_df['cumulative_pnl'] = backtest_df['pnl'].cumsum()
        fig3 = px.line(backtest_df, x=backtest_df.index, y='cumulative_pnl', title='Cumulative PnL Over Backtest')
        st.plotly_chart(fig3, use_container_width=True)

        # PnL distribution
        fig4 = px.histogram(backtest_df[backtest_df['pnl'] != 0], x='pnl', nbins=50, title='PnL Distribution')
        st.plotly_chart(fig4, use_container_width=True)

    except FileNotFoundError:
        st.info("Run the backtest mode in sensex_trading_model.py to generate backtest_results.csv for analysis.")
    except Exception as e:
        st.error(f"Error loading backtest data: {e}")

with tab4:
    # --- Prompt Tracking Dashboard ---
    st.header("📝 AI Prompt Tracking")
    prompt_tracking_dashboard()