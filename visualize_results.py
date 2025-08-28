# visualize_results.py - Script to visualize trading results

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json

def parse_log_file(log_file):
    """Parse the trading system log file to extract trade data"""
    print(f"Parsing log file: {log_file}")
    
    trades = []
    positions = []
    capital_history = []
    daily_pnl = []
    
    # Regular expressions for parsing log entries
    trade_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - (PAPER TRADE|REAL TRADE): (BUY|SELL) (\d+) shares at ₹([\d.]+) \(Position size: ₹([\d.]+)\)"
    position_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Open (BUY|SELL) position. Current P&L: ₹([\d.-]+) \(([\d.-]+)%\)"
    exit_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - (Stop loss|Target) hit for (BUY|SELL) position. P&L: ₹([\d.-]+) \(([\d.-]+)%\)"
    capital_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Calculated position size: ₹([\d.]+) \(Capital: ₹([\d.]+), Daily P&L: ₹([\d.-]+)\)"
    
    with open(log_file, 'r') as f:
        for line in f:
            # Parse trade entries
            trade_match = re.search(trade_pattern, line)
            if trade_match:
                timestamp = datetime.strptime(trade_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
                trade_type = trade_match.group(2)
                direction = trade_match.group(3)
                quantity = int(trade_match.group(4))
                price = float(trade_match.group(5))
                position_size = float(trade_match.group(6))
                
                trades.append({
                    'timestamp': timestamp,
                    'type': trade_type,
                    'direction': direction,
                    'quantity': quantity,
                    'price': price,
                    'position_size': position_size,
                    'status': 'OPEN'
                })
            
            # Parse position updates
            position_match = re.search(position_pattern, line)
            if position_match:
                timestamp = datetime.strptime(position_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
                direction = position_match.group(2)
                pnl = float(position_match.group(3))
                pnl_percent = float(position_match.group(4))
                
                positions.append({
                    'timestamp': timestamp,
                    'direction': direction,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'status': 'OPEN'
                })
            
            # Parse exit events
            exit_match = re.search(exit_pattern, line)
            if exit_match:
                timestamp = datetime.strptime(exit_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
                exit_reason = exit_match.group(2)
                direction = exit_match.group(3)
                pnl = float(exit_match.group(4))
                pnl_percent = float(exit_match.group(5))
                
                # Update the corresponding trade status
                for trade in reversed(trades):
                    if trade['direction'] == direction and trade['status'] == 'OPEN':
                        trade['status'] = 'CLOSED'
                        trade['exit_timestamp'] = timestamp
                        trade['exit_reason'] = exit_reason
                        trade['pnl'] = pnl
                        trade['pnl_percent'] = pnl_percent
                        break
            
            # Parse capital updates
            capital_match = re.search(capital_pattern, line)
            if capital_match:
                timestamp = datetime.strptime(capital_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
                position_size = float(capital_match.group(2))
                capital = float(capital_match.group(3))
                daily_pnl_value = float(capital_match.group(4))
                
                capital_history.append({
                    'timestamp': timestamp,
                    'capital': capital
                })
                
                daily_pnl.append({
                    'timestamp': timestamp,
                    'daily_pnl': daily_pnl_value
                })
    
    return {
        'trades': trades,
        'positions': positions,
        'capital_history': capital_history,
        'daily_pnl': daily_pnl
    }

def visualize_trading_results(data):
    """Create visualizations of trading results"""
    if not data['trades']:
        print("No trade data found in the log file.")
        return
    
    # Convert to DataFrames
    trades_df = pd.DataFrame(data['trades'])
    capital_df = pd.DataFrame(data['capital_history'])
    daily_pnl_df = pd.DataFrame(data['daily_pnl'])
    
    # Create output directory if it doesn't exist
    output_dir = "trading_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Set up the figure style
    plt.style.use('ggplot')
    
    # 1. Visualize trades (buy/sell points)
    if not trades_df.empty and 'exit_timestamp' in trades_df.columns:
        closed_trades = trades_df[trades_df['status'] == 'CLOSED'].copy()
        if not closed_trades.empty:
            plt.figure(figsize=(12, 6))
            
            # Plot buy trades
            buy_trades = closed_trades[closed_trades['direction'] == 'BUY']
            if not buy_trades.empty:
                plt.scatter(buy_trades['timestamp'], buy_trades['price'], 
                           color='green', marker='^', s=100, label='Buy')
            
            # Plot sell trades
            sell_trades = closed_trades[closed_trades['direction'] == 'SELL']
            if not sell_trades.empty:
                plt.scatter(sell_trades['timestamp'], sell_trades['price'], 
                           color='red', marker='v', s=100, label='Sell')
            
            # Plot exit points
            plt.scatter(closed_trades['exit_timestamp'], 
                       closed_trades['price'] * (1 + closed_trades['pnl_percent']/100), 
                       color='blue', marker='o', s=50, label='Exit')
            
            plt.title('Trading Activity')
            plt.xlabel('Time')
            plt.ylabel('Price (₹)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            # Format x-axis to show dates nicely
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.gca().xaxis.set_major_locator(mdates.HourLocator())
            
            # Save the figure
            plt.savefig(os.path.join(output_dir, 'trades.png'))
            print(f"Saved trades visualization to {os.path.join(output_dir, 'trades.png')}")
    
    # 2. Visualize capital over time
    if not capital_df.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(capital_df['timestamp'], capital_df['capital'], 'b-', linewidth=2)
        plt.title('Capital Over Time')
        plt.xlabel('Time')
        plt.ylabel('Capital (₹)')
        plt.grid(True)
        plt.tight_layout()
        
        # Format x-axis to show dates nicely
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
        
        # Save the figure
        plt.savefig(os.path.join(output_dir, 'capital.png'))
        print(f"Saved capital visualization to {os.path.join(output_dir, 'capital.png')}")
    
    # 3. Visualize daily P&L
    if not daily_pnl_df.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(daily_pnl_df['timestamp'], daily_pnl_df['daily_pnl'], 'g-', linewidth=2)
        plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        plt.title('Daily P&L')
        plt.xlabel('Time')
        plt.ylabel('P&L (₹)')
        plt.grid(True)
        plt.tight_layout()
        
        # Format x-axis to show dates nicely
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator())
        
        # Save the figure
        plt.savefig(os.path.join(output_dir, 'daily_pnl.png'))
        print(f"Saved daily P&L visualization to {os.path.join(output_dir, 'daily_pnl.png')}")
    
    # 4. Create a trade summary
    if not trades_df.empty:
        closed_trades = trades_df[trades_df['status'] == 'CLOSED'].copy()
        if not closed_trades.empty:
            # Calculate trade statistics
            total_trades = len(closed_trades)
            winning_trades = len(closed_trades[closed_trades['pnl'] > 0])
            losing_trades = len(closed_trades[closed_trades['pnl'] <= 0])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            total_pnl = closed_trades['pnl'].sum()
            avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
            avg_win = closed_trades[closed_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = closed_trades[closed_trades['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
            
            # Create a summary dictionary
            summary = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'avg_pnl': avg_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss
            }
            
            # Save the summary as JSON
            with open(os.path.join(output_dir, 'trade_summary.json'), 'w') as f:
                json.dump(summary, f, indent=4)
            
            print(f"Saved trade summary to {os.path.join(output_dir, 'trade_summary.json')}")
            
            # Print the summary
            print("\n===== Trade Summary =====")
            print(f"Total Trades: {total_trades}")
            print(f"Winning Trades: {winning_trades} ({win_rate:.2f}%)")
            print(f"Losing Trades: {losing_trades} ({100-win_rate:.2f}%)")
            print(f"Total P&L: ₹{total_pnl:.2f}")
            print(f"Average P&L per Trade: ₹{avg_pnl:.2f}")
            if winning_trades > 0:
                print(f"Average Win: ₹{avg_win:.2f}")
            if losing_trades > 0:
                print(f"Average Loss: ₹{avg_loss:.2f}")
            
            # Create a pie chart of win/loss ratio
            plt.figure(figsize=(8, 8))
            plt.pie([winning_trades, losing_trades], 
                   labels=['Winning Trades', 'Losing Trades'],
                   colors=['green', 'red'],
                   autopct='%1.1f%%',
                   startangle=90)
            plt.axis('equal')
            plt.title('Win/Loss Ratio')
            plt.tight_layout()
            
            # Save the figure
            plt.savefig(os.path.join(output_dir, 'win_loss_ratio.png'))
            print(f"Saved win/loss ratio visualization to {os.path.join(output_dir, 'win_loss_ratio.png')}")

def find_latest_log_file():
    """Find the latest log file in the current directory"""
    log_files = [f for f in os.listdir('.') if f.startswith('trade_log_') and f.endswith('.txt')]
    if not log_files:
        return None
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return log_files[0]

def main():
    print("\n===== Trading Results Visualizer =====\n")
    
    # Find the latest log file
    latest_log = find_latest_log_file()
    if not latest_log:
        print("No log files found. Please run the trading system first.")
        return
    
    # Ask user if they want to use the latest log file or specify a different one
    print(f"Latest log file found: {latest_log}")
    use_latest = input("Do you want to use this log file? (y/n): ").lower()
    
    if use_latest != 'y':
        log_file = input("Enter the path to the log file you want to analyze: ")
        if not os.path.exists(log_file):
            print(f"Error: File {log_file} not found.")
            return
    else:
        log_file = latest_log
    
    # Parse the log file
    data = parse_log_file(log_file)
    
    # Visualize the results
    visualize_trading_results(data)
    
    print("\nVisualization complete! Check the 'trading_results' directory for the output files.")

if __name__ == "__main__":
    main()