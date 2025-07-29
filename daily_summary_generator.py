import os

# Add the path to the MSYS2 MinGW64 bin directory
# This is crucial for WeasyPrint to find its GTK3+ dependencies on Windows
# Assuming default MSYS2 installation path
if os.name == 'nt':  # Check if the operating system is Windows
    msys2_mingw_bin_path = r'C:\msys64\mingw64\bin'
    if os.path.exists(msys2_mingw_bin_path):
        os.add_dll_directory(msys2_mingw_bin_path)
    else:
        print(f"Warning: MSYS2 MinGW64 bin directory not found at {msys2_mingw_bin_path}. WeasyPrint might fail.")

import json
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt
import seaborn as sns
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

class DailySummaryGenerator:
    def __init__(self, logs_dir='logs', reports_dir='reports'):
        self.logs_dir = logs_dir
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def collect_summary_data(self):
        # 1. Date & Report Timestamp
        report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Active Agents & Regimes Used (from agent_rotation_log.csv)
        agent_rotation_log_path = os.path.join(self.logs_dir, 'agent_rotation_log.csv')
        agent_rotation_df = pd.read_csv(agent_rotation_log_path) if os.path.exists(agent_rotation_log_path) else pd.DataFrame()

        # 3. Detected Drift Summary (from retrain_log.csv)
        retrain_log_path = os.path.join(self.logs_dir, 'retrain_log.csv')
        retrain_df = pd.read_csv(retrain_log_path) if os.path.exists(retrain_log_path) else pd.DataFrame()

        # 4. Top Signal of the Day (from leaderboard.csv)
        leaderboard_path = 'leaderboard.csv' # Assuming it's in the root directory
        leaderboard_df = pd.read_csv(leaderboard_path) if os.path.exists(leaderboard_path) else pd.DataFrame()
        top_strategy = leaderboard_df.sort_values(by='pnl', ascending=False).iloc[0] if not leaderboard_df.empty else None

        # Placeholder for Aggregated Reward/PnL Graphs
        # This will involve more complex logic to generate plots from historical data
        plots_data = self.generate_performance_plots(leaderboard_df)
        insights = self.generate_insights(agent_rotation_df, retrain_df, top_strategy)

        return {
            'report_timestamp': report_timestamp,
            'agent_rotation_df': agent_rotation_df.to_html(index=False) if not agent_rotation_df.empty else "<p>No agent rotation data available.</p>",
            'retrain_df': retrain_df.to_html(index=False) if not retrain_df.empty else "<p>No retrain data available.</p>",
            'top_strategy': top_strategy.to_frame().to_html() if top_strategy is not None else "<p>No top strategy data available.</p>",
            'plots_data': plots_data,
            'insights': insights
        }

    def generate_performance_plots(self, leaderboard_df):
        plot_paths = {'pnl_plot_path': None, 'sharpe_plot_path': None}
        if leaderboard_df.empty:
            return plot_paths

        # Ensure 'reports' directory exists for plots
        os.makedirs(self.reports_dir, exist_ok=True)

        # PnL Plot
        plt.figure(figsize=(10, 6))
        sns.barplot(x='strategy_name', y='pnl', data=leaderboard_df)
        plt.title('PnL per Strategy')
        plt.xlabel('Strategy Name')
        plt.ylabel('PnL')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        pnl_plot_path = os.path.join(self.reports_dir, 'pnl_per_strategy.png')
        plt.savefig(pnl_plot_path)
        plt.close()
        plot_paths['pnl_plot_path'] = pnl_plot_path

        # Sharpe Ratio Plot
        plt.figure(figsize=(10, 6))
        sns.barplot(x='strategy_name', y='sharpe_ratio', data=leaderboard_df)
        plt.title('Sharpe Ratio per Strategy')
        plt.xlabel('Strategy Name')
        plt.ylabel('Sharpe Ratio')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        sharpe_plot_path = os.path.join(self.reports_dir, 'sharpe_ratio_per_strategy.png')
        plt.savefig(sharpe_plot_path)
        plt.close()
        plot_paths['sharpe_plot_path'] = sharpe_plot_path

        return plot_paths

    def generate_insights(self, agent_rotation_df, retrain_df, top_strategy):
        insights = []

        if not agent_rotation_df.empty:
            latest_regime = agent_rotation_df.iloc[-1]['regime']
            latest_agent = agent_rotation_df.iloc[-1]['agent_name']
            insights.append(f"The system is currently operating under the '{latest_regime}' regime, managed by '{latest_agent}'.")

        if not retrain_df.empty:
            recent_retrains = retrain_df[retrain_df['timestamp'].str.contains(datetime.date.today().strftime('%Y-%m-%d'))]
            if not recent_retrains.empty:
                insights.append(f"Detected {len(recent_retrains)} agent retraining event(s) today due to performance drift.")
                for _, row in recent_retrains.iterrows():
                    insights.append(f"- Agent '{row['agent_name']}' for regime '{row['regime']}' was retrained at {row['timestamp']}.")
            else:
                insights.append("No agent retraining events detected today.")
        else:
            insights.append("No retrain log data available to analyze drift.")

        if top_strategy is not None:
            insights.append(f"Today's top performing strategy is '{top_strategy['strategy_name']}' with a PnL of {top_strategy['pnl']:.2f} and Sharpe Ratio of {top_strategy['sharpe_ratio']:.2f}.")
        else:
            insights.append("No top strategy data available from the leaderboard.")

        return " ".join(insights)

    def render_summary_report(self, data):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.from_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daily Summary Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #555; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .insight-box { background-color: #e6f7ff; border: 1px solid #91d5ff; padding: 15px; margin-top: 20px; border-radius: 5px; }
                img { max-width: 100%; height: auto; margin-top: 10px; }
            </style>
        </head>
        <body>
            <h1>Daily Summary Report</h1>
            <p><strong>Report Generated:</strong> {{ report_timestamp }}</p>

            <h2>Active Agents & Regimes Used</h2>
            {{ agent_rotation_df }}

            <h2>Detected Drift Summary</h2>
            {{ retrain_df }}

            <h2>Top Strategy of the Day</h2>
            {{ top_strategy }}

            <h2>Performance Plots</h2>
            {% if plots_data.pnl_plot_path %}
                <h3>PnL Plot</h3>
                <img src="{{ plots_data.pnl_plot_path }}" alt="PnL Plot">
            {% else %}
                <p>PnL plot not available.</p>
            {% endif %}
            {% if plots_data.sharpe_plot_path %}
                <h3>Sharpe Ratio Plot</h3>
                <img src="{{ plots_data.sharpe_plot_path }}" alt="Sharpe Ratio Plot">
            {% else %}
                <p>Sharpe Ratio plot not available.</p>
            {% endif %}

            <h2>Summary Box (Insights)</h2>
            <div class="insight-box">
                <p>{{ insights }}</p>
            </div>
        </body>
        </html>
        """
        )
        return template.render(data)

    def export_pdf_report(self, html_content, filename):
        # This function requires a PDF rendering library like WeasyPrint or ReportLab
        # For now, it will just save the HTML content.
        HTML(string=html_content).write_pdf(filename)
        print(f"PDF report saved to {filename}.")

    def store_output(self, html_content):
        report_filename_html = os.path.join(self.reports_dir, f"daily_summary_{date.today().strftime('%Y%m%d')}.html")
        report_filename_pdf = os.path.join(self.reports_dir, f"daily_summary_{date.today().strftime('%Y%m%d')}.pdf")

        with open(report_filename_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Daily summary HTML report saved to {report_filename_html}")

        self.export_pdf_report(html_content, report_filename_pdf)

if __name__ == '__main__':
    generator = DailySummaryGenerator()
    summary_data = generator.collect_summary_data()
    html_report = generator.render_summary_report(summary_data)
    generator.store_output(html_report)

    print("Daily summary report generation complete.")