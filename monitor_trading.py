# monitor_trading.py - Simple script to monitor the trading system in real-time

import os
import re
import time
import json
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# Initialize colorama
colorama.init()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def find_latest_log_file():
    """Find the latest log file in the current directory"""
    log_files = [f for f in os.listdir('.') if f.startswith('trade_log_') and f.endswith('.txt')]
    if not log_files:
        return None
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return log_files[0]

def parse_log_file(log_file):
    """Parse the trading system log file to extract the latest information"""
    if not os.path.exists(log_file):
        return None
    
    # Regular expressions for parsing log entries
    capital_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Calculated position size: ₹([\d.]+) \(Capital: ₹([\d.]+), Daily P&L: ₹([\d.-]+)\)"
    trade_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - (PAPER TRADE|REAL TRADE): (BUY|SELL) (\d+) shares at ₹([\d.]+) \(Position size: ₹([\d.]+)\)"
    position_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Open (BUY|SELL) position. Current P&L: ₹([\d.-]+) \(([\d.-]+)%\)"
    exit_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - (Stop loss|Target) hit for (BUY|SELL) position. P&L: ₹([\d.-]+) \(([\d.-]+)%\)"
    prediction_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Prediction: ([\d.-]+), Confidence: ([\d.]+)"
    market_data_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - Market data: (.*)"
    
    # Initialize data structures
    latest_capital = None
    latest_daily_pnl = None
    latest_prediction = None
    latest_confidence = None
    latest_market_data = None
    open_positions = []
    recent_trades = []
    recent_exits = []
    
    # Read the log file from the end to get the most recent entries
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Process the last 1000 lines (or fewer if the file is smaller)
    for line in lines[-1000:]:
        # Parse capital updates
        capital_match = re.search(capital_pattern, line)
        if capital_match:
            timestamp = datetime.strptime(capital_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
            position_size = float(capital_match.group(2))
            capital = float(capital_match.group(3))
            daily_pnl = float(capital_match.group(4))
            
            latest_capital = capital
            latest_daily_pnl = daily_pnl
        
        # Parse trade entries
        trade_match = re.search(trade_pattern, line)
        if trade_match:
            timestamp = datetime.strptime(trade_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
            trade_type = trade_match.group(2)
            direction = trade_match.group(3)
            quantity = int(trade_match.group(4))
            price = float(trade_match.group(5))
            position_size = float(trade_match.group(6))
            
            recent_trades.append({
                'timestamp': timestamp,
                'type': trade_type,
                'direction': direction,
                'quantity': quantity,
                'price': price,
                'position_size': position_size
            })
            
            # Keep only the 5 most recent trades
            if len(recent_trades) > 5:
                recent_trades.pop(0)
        
        # Parse position updates
        position_match = re.search(position_pattern, line)
        if position_match:
            timestamp = datetime.strptime(position_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
            direction = position_match.group(2)
            pnl = float(position_match.group(3))
            pnl_percent = float(position_match.group(4))
            
            # Update or add position
            position_found = False
            for pos in open_positions:
                if pos['direction'] == direction:
                    pos['timestamp'] = timestamp
                    pos['pnl'] = pnl
                    pos['pnl_percent'] = pnl_percent
                    position_found = True
                    break
            
            if not position_found:
                open_positions.append({
                    'timestamp': timestamp,
                    'direction': direction,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent
                })
        
        # Parse exit events
        exit_match = re.search(exit_pattern, line)
        if exit_match:
            timestamp = datetime.strptime(exit_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
            exit_reason = exit_match.group(2)
            direction = exit_match.group(3)
            pnl = float(exit_match.group(4))
            pnl_percent = float(exit_match.group(5))
            
            recent_exits.append({
                'timestamp': timestamp,
                'exit_reason': exit_reason,
                'direction': direction,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            })
            
            # Keep only the 5 most recent exits
            if len(recent_exits) > 5:
                recent_exits.pop(0)
            
            # Remove from open positions
            for i, pos in enumerate(open_positions):
                if pos['direction'] == direction:
                    open_positions.pop(i)
                    break
        
        # Parse prediction updates
        prediction_match = re.search(prediction_pattern, line)
        if prediction_match:
            timestamp = datetime.strptime(prediction_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
            prediction = float(prediction_match.group(2))
            confidence = float(prediction_match.group(3))
            
            latest_prediction = prediction
            latest_confidence = confidence
        
        # Parse market data
        market_data_match = re.search(market_data_pattern, line)
        if market_data_match:
            timestamp = datetime.strptime(market_data_match.group(1), '%Y-%m-%d %H:%M:%S,%f')
            market_data_json = market_data_match.group(2)
            
            try:
                latest_market_data = json.loads(market_data_json)
            except:
                pass
    
    return {
        'latest_capital': latest_capital,
        'latest_daily_pnl': latest_daily_pnl,
        'latest_prediction': latest_prediction,
        'latest_confidence': latest_confidence,
        'latest_market_data': latest_market_data,
        'open_positions': open_positions,
        'recent_trades': recent_trades,
        'recent_exits': recent_exits,
        'last_update': datetime.now()
    }

def display_dashboard(data):
    """Display a simple dashboard with the current trading system status"""
    if not data:
        print(f"{Fore.RED}No data available. Make sure the trading system is running.{Style.RESET_ALL}")
        return
    
    clear_screen()
    
    # Header
    print(f"{Fore.CYAN}===================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT} MINIMAL TRADING SYSTEM MONITOR {Style.RESET_ALL}")
    print(f"{Fore.CYAN}===================================={Style.RESET_ALL}")
    print(f"Last Update: {data['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Capital and P&L
    print(f"{Fore.YELLOW}{Style.BRIGHT}ACCOUNT SUMMARY{Style.RESET_ALL}")
    if data['latest_capital'] is not None:
        print(f"Current Capital: {Fore.GREEN}₹{data['latest_capital']:.2f}{Style.RESET_ALL}")
    else:
        print(f"Current Capital: {Fore.RED}Not available{Style.RESET_ALL}")
    
    if data['latest_daily_pnl'] is not None:
        if data['latest_daily_pnl'] >= 0:
            print(f"Daily P&L: {Fore.GREEN}₹{data['latest_daily_pnl']:.2f}{Style.RESET_ALL}")
        else:
            print(f"Daily P&L: {Fore.RED}₹{data['latest_daily_pnl']:.2f}{Style.RESET_ALL}")
    else:
        print(f"Daily P&L: {Fore.RED}Not available{Style.RESET_ALL}")
    print()
    
    # Latest Prediction
    print(f"{Fore.YELLOW}{Style.BRIGHT}LATEST PREDICTION{Style.RESET_ALL}")
    if data['latest_prediction'] is not None and data['latest_confidence'] is not None:
        prediction_direction = "BUY" if data['latest_prediction'] > 0 else "SELL"
        prediction_color = Fore.GREEN if prediction_direction == "BUY" else Fore.RED
        print(f"Direction: {prediction_color}{prediction_direction}{Style.RESET_ALL}")
        print(f"Confidence: {data['latest_confidence']:.2f}")
    else:
        print(f"No prediction data available")
    print()
    
    # Market Data
    print(f"{Fore.YELLOW}{Style.BRIGHT}MARKET DATA{Style.RESET_ALL}")
    if data['latest_market_data']:
        for key, value in data['latest_market_data'].items():
            print(f"{key}: {value}")
    else:
        print(f"No market data available")
    print()
    
    # Open Positions
    print(f"{Fore.YELLOW}{Style.BRIGHT}OPEN POSITIONS ({len(data['open_positions'])}){Style.RESET_ALL}")
    if data['open_positions']:
        for pos in data['open_positions']:
            direction_color = Fore.GREEN if pos['direction'] == "BUY" else Fore.RED
            pnl_color = Fore.GREEN if pos['pnl'] >= 0 else Fore.RED
            print(f"{direction_color}{pos['direction']}{Style.RESET_ALL} - P&L: {pnl_color}₹{pos['pnl']:.2f} ({pos['pnl_percent']:.2f}%){Style.RESET_ALL} - Updated: {pos['timestamp'].strftime('%H:%M:%S')}")
    else:
        print(f"No open positions")
    print()
    
    # Recent Trades
    print(f"{Fore.YELLOW}{Style.BRIGHT}RECENT TRADES ({len(data['recent_trades'])}){Style.RESET_ALL}")
    if data['recent_trades']:
        for trade in reversed(data['recent_trades']):
            direction_color = Fore.GREEN if trade['direction'] == "BUY" else Fore.RED
            print(f"{trade['timestamp'].strftime('%H:%M:%S')} - {trade['type']}: {direction_color}{trade['direction']}{Style.RESET_ALL} {trade['quantity']} shares at ₹{trade['price']:.2f} (₹{trade['position_size']:.2f})")
    else:
        print(f"No recent trades")
    print()
    
    # Recent Exits
    print(f"{Fore.YELLOW}{Style.BRIGHT}RECENT EXITS ({len(data['recent_exits'])}){Style.RESET_ALL}")
    if data['recent_exits']:
        for exit in reversed(data['recent_exits']):
            direction_color = Fore.GREEN if exit['direction'] == "BUY" else Fore.RED
            pnl_color = Fore.GREEN if exit['pnl'] >= 0 else Fore.RED
            reason_color = Fore.GREEN if exit['exit_reason'] == "Target" else Fore.RED
            print(f"{exit['timestamp'].strftime('%H:%M:%S')} - {reason_color}{exit['exit_reason']}{Style.RESET_ALL} hit for {direction_color}{exit['direction']}{Style.RESET_ALL} - P&L: {pnl_color}₹{exit['pnl']:.2f} ({exit['pnl_percent']:.2f}%){Style.RESET_ALL}")
    else:
        print(f"No recent exits")
    print()
    
    print(f"{Fore.CYAN}===================================={Style.RESET_ALL}")
    print(f"Press Ctrl+C to exit")

def monitor_trading_system():
    """Monitor the trading system in real-time"""
    try:
        while True:
            # Find the latest log file
            log_file = find_latest_log_file()
            if not log_file:
                clear_screen()
                print(f"{Fore.RED}No log files found. Please run the trading system first.{Style.RESET_ALL}")
                time.sleep(5)
                continue
            
            # Parse the log file
            data = parse_log_file(log_file)
            
            # Display the dashboard
            display_dashboard(data)
            
            # Wait before refreshing
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitor stopped.{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f"{Fore.CYAN}Starting trading system monitor...{Style.RESET_ALL}")
    monitor_trading_system()