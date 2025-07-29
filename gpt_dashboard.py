import streamlit as st
import pandas as pd
import os
import re
import yaml
import graphviz
import json
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import io
import numpy as np
import plotly.express as px
from prompt_score_evaluator import PromptScoreEvaluator
from theme_regime_analyzer import ThemeRegimeAnalyzer

# --- Configuration --- #
GPT_LOGS_DIR = 'gpt_logs/'
GPT_OUTPUTS_DIR = 'gpt_outputs/'
REFINED_STRATEGIES_DIR = 'refined_strategies/'
LEADERBOARD_PATH = 'leaderboard.csv'
BACKTEST_RESULTS_PATH = 'gpt_backtest_results.csv'
MODEL_LOG_PATH = 'model_log.txt'
TRADE_LOG_PATH = 'trade_log.csv'

st.set_page_config(layout="wide", page_title="Red Machine Intelligence Dashboard")

# --- Helper Functions --- #
def load_gpt_logs():
    logs = []
    for filename in os.listdir(GPT_LOGS_DIR):
        if filename.endswith('.log'):
            filepath = os.path.join(GPT_LOGS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                logs.append({'filename': filename, 'content': content})
    return logs

def extract_yaml_from_log(log_content):
    match = re.search(r'```(?:yaml)?\s*\n(.*?)\n```', log_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def load_leaderboard():
    if os.path.exists(LEADERBOARD_PATH):
        return pd.read_csv(LEADERBOARD_PATH)
    return pd.DataFrame()

def load_backtest_results():
    if os.path.exists(BACKTEST_RESULTS_PATH):
        return pd.read_csv(BACKTEST_RESULTS_PATH)
    return pd.DataFrame()

def load_top_strategy():
    if os.path.exists(LEADERBOARD_PATH):
        leaderboard_df = pd.read_csv(LEADERBOARD_PATH)
        if not leaderboard_df.empty:
            # Assuming 'composite_score' is the metric for ranking
            top_strategy_row = leaderboard_df.sort_values(by='pnl', ascending=False).iloc[0]
            strategy_name = top_strategy_row.get('strategy_name', 'N/A')
            # You might need to construct the path to the actual strategy YAML file
            # based on how strategy_name maps to filenames in refined_strategies/
            return strategy_name, top_strategy_row.to_dict()
    return None, {}

def load_latest_trades(num_trades=3):
    if os.path.exists(TRADE_LOG_PATH):
        trades_df = pd.read_csv(TRADE_LOG_PATH, header=None, names=[
            "Timestamp", "Option Type", "Strike", "Expiry", "LTP", "Signal", "Status"
        ])
        trades_df['Timestamp'] = pd.to_datetime(trades_df['Timestamp'])
        return trades_df.tail(num_trades)
    return pd.DataFrame()

def load_active_agent_status():
    status_path = 'active_agent_status.json'
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            return json.load(f)
    return None

# --- Dashboard UI --- #
st.title("🧠 Red Machine Intelligence Dashboard")

st.sidebar.title("Navigation")
selection = st.sidebar.radio(
    "Go to",
    [
        'Prompt Tree Mapping',
        'Signal Dashboard Panel',
        'Interactive SENSEX Scanner',
        'Strategy Leaderboard',
        'Research & Analytics',
    'Theme x Regime Leaderboard',
    'RL Agent Status',
    'RL Agent Rotation Log',
    'RL Agent Overview'
    ]
)

if selection == 'RL Agent Status':
    st.header("RL Agent Status")
    st.write("Monitor the currently active RL agent and its regime context.")

    st.subheader("Currently Active Agent")
    # Placeholder for displaying the currently active agent and regime context
    active_agent_status = load_active_agent_status()
    if active_agent_status:
        st.info(f"Currently active agent: **{active_agent_status['active_agent_name']}**")
        st.info(f"Regime context: **{active_agent_status['active_regime']}**")
    else:
        st.info("No active agent status found. Run `regime_router_executor.py` to determine the active agent.")


    st.subheader("Reward vs Time by Active Regime")
    st.write("This chart will display the reward vs time for the active regime.")
    # Placeholder for chart display
    st.warning("Historical reward data needs to be integrated for this chart.")



elif selection == 'RL Agent Rotation Log':
    st.header("RL Agent Rotation Log")
    st.write("Visualize the history of RL agent rotations, regime changes, and associated performance.")

    log_file_path = 'logs/agent_rotation_log.csv'
    if os.path.exists(log_file_path):
        try:
            rotation_df = pd.read_csv(log_file_path)
            st.subheader("Agent Rotation History")
            st.dataframe(rotation_df)

            # Plotting Reward vs Time
            if not rotation_df.empty and 'timestamp' in rotation_df.columns and 'reward' in rotation_df.columns:
                rotation_df['timestamp'] = pd.to_datetime(rotation_df['timestamp'])
                st.subheader("Reward vs Time by Agent and Regime")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.lineplot(data=rotation_df, x='timestamp', y='reward', hue='model_loaded', style='regime', marker='o', ax=ax)
                ax.set_title('Reward Over Time by Active Agent and Regime')
                ax.set_xlabel('Time')
                ax.set_ylabel('Reward')
                ax.tick_params(axis='x', rotation=45)
                st.pyplot(fig)
            else:
                st.info("Not enough data in the log file to plot Reward vs Time.")

        except pd.errors.EmptyDataError:
            st.info("The agent rotation log file is empty.")
        except Exception as e:
            st.error(f"Error loading or processing agent rotation log: {e}")
    else:
        st.info("Agent rotation log file not found. Run `regime_router_executor.py` to generate the log.")

elif selection == 'RL Agent Overview':
    st.header("RL Agent Performance Analytics Board")
    st.write("Visually summarize per-agent performance, model drift, and agent fitness vs regime.")

    log_file_path = 'logs/agent_rotation_log.csv'
    if os.path.exists(log_file_path):
        try:
            rotation_df = pd.read_csv(log_file_path)
            if not rotation_df.empty:
                # Ensure 'timestamp' is datetime and 'reward' and 'pnl' are numeric
                rotation_df['timestamp'] = pd.to_datetime(rotation_df['timestamp'])
                rotation_df['reward'] = pd.to_numeric(rotation_df['reward'], errors='coerce').fillna(0)
                rotation_df['pnl'] = pd.to_numeric(rotation_df['pnl'], errors='coerce').fillna(0)

                st.subheader("Agent Aggregate Stats Table")
                # Compute aggregate stats per agent
                agent_stats = rotation_df.groupby('model_loaded').agg(
                    total_activations=('model_loaded', 'count'),
                    mean_reward=('reward', 'mean'),
                    total_pnl=('pnl', 'sum'),
                    mean_pnl=('pnl', 'mean')
                ).reset_index()

                # Determine dominant regime for each agent
                dominant_regime = rotation_df.groupby('model_loaded')['regime'].agg(lambda x: x.mode()[0] if not x.mode().empty else 'N/A').reset_index()
                agent_stats = pd.merge(agent_stats, dominant_regime, on='model_loaded', how='left')
                agent_stats.rename(columns={'model_loaded': 'Agent Name', 'total_activations': 'Total Activations', 'mean_reward': 'Mean Reward', 'total_pnl': 'Total PnL', 'mean_pnl': 'Mean PnL', 'regime': 'Dominant Regime'}, inplace=True)
                st.dataframe(agent_stats)

                st.subheader("Reward Over Time by Agent")
                fig_reward_time = px.line(rotation_df, x='timestamp', y='reward', color='model_loaded', title='Reward Over Time by Agent')
                st.plotly_chart(fig_reward_time)

                st.subheader("Aggregated Rewards by Regime and Agent (Heatmap)")
                # Aggregate mean reward by regime and agent
                heatmap_data = rotation_df.groupby(['regime', 'model_loaded'])['reward'].mean().unstack().fillna(0)
                fig_heatmap = px.imshow(heatmap_data, text_auto=True, aspect="auto",
                                        title="Mean Reward by Regime and Agent",
                                        labels=dict(x="Agent Name", y="Regime", color="Mean Reward"))
                st.plotly_chart(fig_heatmap)

            else:
                st.info("The agent rotation log file is empty or contains no data.")

        except pd.errors.EmptyDataError:
            st.info("The agent rotation log file is empty.")
        except Exception as e:
            st.error(f"Error loading or processing agent rotation log: {e}")
    else:
        st.info("Agent rotation log file not found. Run `regime_router_executor.py` to generate the log.")


elif selection == 'Prompt Tree Mapping':
    st.header("Prompt Tree Mapping")
    st.write("Visualize the evolution of prompts and their connection to top-ranked strategies here.")
    # Placeholder for prompt tree visualization logic
    st.write("This section will visualize the evolution of prompts.")

    PROMPT_EVOLUTION_DIR = 'gpt_logs/' # Assuming audit files are in gpt_logs
    if os.path.exists(PROMPT_EVOLUTION_DIR):
        audit_files = [f for f in os.listdir(PROMPT_EVOLUTION_DIR) if f.startswith('audit_') and f.endswith('.json')]
        if audit_files:
            graph = graphviz.Digraph(comment='Prompt Evolution Tree', graph_attr={'rankdir': 'LR'})

            # Initialize PromptScoreEvaluator and load scores
            score_evaluator = PromptScoreEvaluator()
            prompt_scores = score_evaluator.evaluate_prompts()

            # Add nodes and edges for each audit file
            for audit_file in audit_files:
                filepath = os.path.join(PROMPT_EVOLUTION_DIR, audit_file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    audit_data = json.load(f)

                prompt_hash = audit_data.get('prompt_hash')
                strategy_name = audit_data.get('strategy_name')

                node_label = f"Prompt: {prompt_hash[:8]}..."
                score_info = ""

                if prompt_hash and prompt_hash in prompt_scores:
                    prompt_detail = prompt_scores[prompt_hash]
                    
                    total_strategy_count = prompt_detail.get('total_strategy_count', 0)
                    avg_net_pnl = prompt_detail.get('avg_net_pnl', 0)
                    avg_sharpe_ratio = prompt_detail.get('avg_sharpe_ratio', 0)
                    victory_rate = prompt_detail.get('victory_rate', 0)

                    score_info = (
                        f"\nStrategies: {total_strategy_count}"
                        f"\nAvg PnL: {avg_net_pnl:.2f}"
                        f"\nAvg Sharpe: {avg_sharpe_ratio:.2f}"
                        f"\nWin %: {victory_rate:.2f}%"
                    )

                graph.node(prompt_hash, node_label + score_info)

                # For now, we'll just add nodes for each prompt_hash found in audit files.
                # The actual "evolution" (edges) would depend on how prompts are linked (parent_hash, etc.)
                # This part needs more sophisticated logic based on your prompt_optimizer's output structure.
                # For demonstration, we'll just show the nodes with scores.

            st.graphviz_chart(graph)
        else:
            st.info("No prompt evolution audit files found. Run `prompt_optimizer.py` to generate them.")
    else:
        st.info("Prompt evolution directory not found. Run `prompt_optimizer.py` to generate audit trails.")

elif selection == 'Signal Dashboard Panel':
    st.header("Signal Dashboard Panel")
    st.write("Display current top strategy, live trade status (last 3 trades), and other signal-related metrics here.")
    # Placeholder for signal dashboard logic

    st.subheader("Current Top Strategy")
    top_strategy_name, top_strategy_metrics = load_top_strategy()
    if top_strategy_name:
        st.write(f"**Strategy Name:** {top_strategy_name}")
        st.json(top_strategy_metrics)
    else:
        st.info("No top strategy found. Run `strategy_scorer.py` to generate the leaderboard.")

    st.subheader("Live Trade Status (Last 3 Trades)")
    latest_trades = load_latest_trades(3)
    if not latest_trades.empty:
        st.dataframe(latest_trades)
    else:
        st.info("No live trade data available. Run `live_signal_executor.py` to generate trade logs.")

    st.subheader("Runbook Access")
    # Logic to open the latest runbook report (e.g., from reports/ directory)
    reports_dir = 'reports/'
    if os.path.exists(reports_dir):
        html_reports = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
        if html_reports:
            latest_report = sorted(html_reports, reverse=True)[0] # Assuming latest is alphabetically last
            report_path = os.path.join(reports_dir, latest_report)
            st.markdown(f"[View Latest Runbook Report]({report_path})")
        else:
            st.info("No HTML runbook reports found in the `reports/` directory.")
    else:
        st.info("Reports directory not found.")

elif selection == 'Interactive SENSEX Scanner':
    st.header("Interactive SENSEX Scanner")
    st.write("Monitor prices, IVs, and potentially embed a terminal panel here.")
    # Placeholder for SENSEX scanner logic

    st.subheader("Real-time SENSEX Data")
    # Placeholder for real-time SENSEX data fetching and display
    st.write("*(Data will be displayed here once integrated with a real-time market data API)*")
    # Example of mock data display
    st.dataframe(pd.DataFrame({
        'Metric': ['SENSEX Index', 'Implied Volatility (IV)', 'Open Interest (OI)'],
        'Value': ['75,000', '15.2%', '1,200,000']
    }))

    st.subheader("Embedded Terminal (Optional)")
    st.info("Embedding a live terminal directly in Streamlit is complex and often not recommended for security/performance. Consider external terminal access.")
    # You could potentially use st.expander and st.code to show command outputs if a backend process is running
    # For example, if you have a script that outputs real-time data to a file, you can read and display that file here.

elif selection == 'Strategy Leaderboard':
    st.header("Strategy Leaderboard")
    leaderboard_df = load_leaderboard()
    if not leaderboard_df.empty:
        st.dataframe(leaderboard_df.sort_values(by='composite_score', ascending=False))
    else:
        st.info("Leaderboard is empty. Run `strategy_scorer.py` to generate it.")

elif selection == 'Theme x Regime Leaderboard':
    st.header("Theme × Regime Leaderboard")
    analyzer = ThemeRegimeAnalyzer()
    correlation_matrix = analyzer.analyze_theme_regime_correlation()
    
    if not correlation_matrix.empty:
        st.write("Performance metrics by theme and market regime:")
        st.dataframe(correlation_matrix.sort_values(by='avg_sharpe', ascending=False))
        
        # Visualize as heatmap
        pivot_df = correlation_matrix.pivot(index='themes', columns='regime', values='avg_sharpe')
        st.write("Heatmap of average Sharpe ratios by theme and regime:")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap='RdYlGn', ax=ax)
        st.pyplot(fig)
    else:
        st.info("No theme-regime correlation data available. Ensure backtest results are labeled with regimes.")

elif selection == 'Research & Analytics':
    st.header("Research & Analytics")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["GPT Logs", "Raw Extracted YAMLs", "Refined Strategies", "Backtest Results", "RL Agent Performance"])

    with tab1:
        st.header("GPT Interaction Logs")
        logs = load_gpt_logs()
        if logs:
            selected_log = st.selectbox("Select a GPT Log File:", [log['filename'] for log in logs])
            if selected_log:
                log_content = next(log['content'] for log in logs if log['filename'] == selected_log)
                st.subheader(f"Content of {selected_log}")
                st.code(log_content, language='text')

                st.subheader("Extracted YAML (Preview)")
                extracted_yaml = extract_yaml_from_log(log_content)
                if extracted_yaml:
                    st.code(extracted_yaml, language='yaml')
                else:
                    st.info("No YAML block found in this log.")

    with tab5:
        st.header("RL Agent Performance")
        st.write("Monitor the performance of the Reinforcement Learning SENSEX Scalper here.")

        st.subheader("Equity Curve & Rolling Sharpe")
        st.info("*(Graphs for equity curve and rolling Sharpe ratio will be displayed here.)*")
        # Placeholder for actual graph generation using matplotlib/plotly
        # Example: st.line_chart(pd.DataFrame({'Equity': [100000, 100100, 100050, 100200]}))

        st.subheader("Live/Paper P&L Tracking")
        st.info("*(Real-time P&L tracking per episode and market regime will be shown here.)*")
        # Placeholder for P&L display
        # Example: st.dataframe(pd.DataFrame({'Episode': [1,2,3], 'PnL': [100, -50, 150]}))

        st.subheader("Visual Decision Paths")
        st.info("*(Visualizations of the RL agent's state-action decisions will be available here.)*")
        # This could involve displaying a simplified state-action tree or highlighting decisions on a price chart


    with tab2:
        st.header("Raw Extracted GPT YAMLs")
        yaml_files = [f for f in os.listdir(GPT_OUTPUTS_DIR) if f.endswith('.yaml')]
        if yaml_files:
            selected_yaml = st.selectbox("Select a Raw Extracted YAML File:", yaml_files)
            if selected_yaml:
                filepath = os.path.join(GPT_OUTPUTS_DIR, selected_yaml)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                st.subheader(f"Content of {selected_yaml}")
                st.code(content, language='yaml')
        else:
            st.info("No raw extracted YAML files found in the `gpt_outputs/` directory. Run `gpt_to_strategy_lab.py` first.")

    with tab3:
        st.header("Refined GPT Strategies")
        refined_yaml_files = [f for f in os.listdir(REFINED_STRATEGIES_DIR) if f.endswith('.yaml')]
        if refined_yaml_files:
            selected_refined_yaml = st.selectbox("Select a Refined Strategy YAML File:", refined_yaml_files)
            if selected_refined_yaml:
                filepath = os.path.join(REFINED_STRATEGIES_DIR, selected_refined_yaml)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                st.subheader(f"Content of {selected_refined_yaml}")
                st.code(content, language='yaml')
        else:
            st.info("No refined strategy YAML files found in the `refined_strategies/` directory. Run `research_refiner.py` or `gpt_to_strategy_lab.py` to generate them.")

    with tab4:
        st.header("GPT Strategy Backtest Results")
        backtest_df = load_backtest_results()
        if not backtest_df.empty:
            st.dataframe(backtest_df)
        else:
            st.info("No backtest results found. Run `gpt_to_strategy_lab.py` to generate them.")

st.markdown("--- \n *Powered by The Red Machine AI Core* ")