#!/usr/bin/env python3
"""
THE RED MACHINE - Complete One-Click Startup System
Starts everything before market opens: Airflow, model, dashboard, Kite integration
"""

import os
import sys
import subprocess
import time
import json
import logging
from pathlib import Path
import signal
import psutil
import argparse
from datetime import datetime, timedelta
import threading
import requests

class CompleteTradingSystem:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.config_file = self.project_dir / "system_config.json"
        self.services = {}
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('system_startup.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Load system configuration"""
        default_config = {
            "capital": 3000,
            "paper_trading": True,
            "kite_api_key": "",
            "kite_access_token": "",
            "airflow_port": 8080,
            "dashboard_port": 8501,
            "auto_start_time": "09:00",
            "market_open": "09:15",
            "market_close": "15:30",
            "services": {
                "airflow": True,
                "dashboard": True,
                "data_simulator": True,
                "model_monitor": True,
                "kite_integration": True
            }
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = default_config
            
    def save_config(self):
        """Save system configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        self.logger.info("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8+ required")
            return False
            
        # Check required packages
        required_packages = [
            'streamlit', 'kiteconnect', 'pandas', 'numpy', 
            'plotly', 'psutil', 'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            self.logger.error(f"Missing packages: {missing_packages}")
            self.logger.info("Installing missing packages...")
            for package in missing_packages:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
                
        return True
        
    def wait_for_market_open(self):
        """Wait for market to open"""
        market_open = datetime.strptime(self.config['market_open'], "%H:%M").time()
        
        while True:
            now = datetime.now().time()
            if now >= market_open:
                self.logger.info("Market is open! Starting system...")
                break
            else:
                time_to_open = datetime.combine(datetime.today(), market_open) - datetime.now()
                self.logger.info(f"Waiting for market open... {time_to_open}")
                time.sleep(60)
                
    def start_airflow(self):
        """Start Airflow services"""
        if not self.config['services']['airflow']:
            self.logger.info("Airflow disabled in config")
            return True
            
        try:
            # Initialize Airflow
            os.environ['AIRFLOW_HOME'] = str(self.project_dir / 'airflow')
            
            # Start Airflow webserver
            webserver_process = subprocess.Popen([
                'airflow', 'webserver', '--port', str(self.config['airflow_port'])
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Start Airflow scheduler
            scheduler_process = subprocess.Popen([
                'airflow', 'scheduler'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.services['airflow_webserver'] = webserver_process
            self.services['airflow_scheduler'] = scheduler_process
            
            # Wait for Airflow to start
            time.sleep(10)
            
            # Check if services are running
            if self.check_service_running('airflow'):
                self.logger.info("Airflow started successfully")
                return True
            else:
                self.logger.error("Failed to start Airflow")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Airflow: {e}")
            return False
            
    def start_dashboard(self):
        """Start enhanced dashboard"""
        if not self.config['services']['dashboard']:
            self.logger.info("Dashboard disabled in config")
            return True
            
        try:
            dashboard_process = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', 
                'enhanced_dashboard.py', 
                '--server.port', str(self.config['dashboard_port']),
                '--server.headless', 'true'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.services['dashboard'] = dashboard_process
            
            # Wait for dashboard to start
            time.sleep(15)
            
            if self.check_service_running('dashboard'):
                self.logger.info(f"Dashboard started on port {self.config['dashboard_port']}")
                return True
            else:
                self.logger.error("Failed to start dashboard")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting dashboard: {e}")
            return False
            
    def start_data_simulator(self):
        """Start data simulator"""
        if not self.config['services']['data_simulator']:
            self.logger.info("Data simulator disabled in config")
            return True
            
        try:
            simulator_process = subprocess.Popen([
                sys.executable, 'data_simulator.py', '--continuous'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.services['data_simulator'] = simulator_process
            
            if self.check_service_running('data_simulator'):
                self.logger.info("Data simulator started")
                return True
            else:
                self.logger.error("Failed to start data simulator")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting data simulator: {e}")
            return False
            
    def retrain_model(self):
        """Retrain the model with 3000 capital"""
        try:
            self.logger.info("Starting model retraining...")
            
            # Run retraining script
            result = subprocess.run([
                sys.executable, 'retrain_model_3000.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Model retrained successfully")
                return True
            else:
                self.logger.error(f"Model retraining failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error retraining model: {e}")
            return False
            
    def run_backtest(self):
        """Run backtest with 3000 capital"""
        try:
            self.logger.info("Running backtest...")
            
            result = subprocess.run([
                sys.executable, 'backtest_3000_capital.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Backtest completed successfully")
                return True
            else:
                self.logger.error(f"Backtest failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error running backtest: {e}")
            return False
            
    def check_service_running(self, service_name: str) -> bool:
        """Check if a service is running"""
        try:
            if service_name == 'airflow':
                response = requests.get(f"http://localhost:{self.config['airflow_port']}", timeout=5)
                return response.status_code == 200
            elif service_name == 'dashboard':
                response = requests.get(f"http://localhost:{self.config['dashboard_port']}", timeout=5)
                return response.status_code == 200
            elif service_name == 'data_simulator':
                # Check if data_simulator.py is running
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if 'data_simulator.py' in str(proc.info['cmdline']):
                        return True
                return False
            return False
        except:
            return False
            
    def setup_kite_config(self):
        """Setup Kite configuration"""
        if not self.config['kite_api_key'] or not self.config['kite_access_token']:
            self.logger.warning("Kite API credentials not configured")
            return False
            
        kite_config = {
            "api_key": self.config['kite_api_key'],
            "access_token": self.config['kite_access_token']
        }
        
        with open('kite_config.json', 'w') as f:
            json.dump(kite_config, f, indent=2)
            
        self.logger.info("Kite configuration saved")
        return True
        
    def start_all_services(self):
        """Start all configured services"""
        self.logger.info("Starting THE RED MACHINE...")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
            
        # Setup Kite
        self.setup_kite_config()
        
        # Run backtest
        if not self.run_backtest():
            self.logger.warning("Backtest failed, continuing...")
            
        # Retrain model
        if not self.retrain_model():
            self.logger.warning("Model retraining failed, continuing...")
            
        # Start services in order
        services_to_start = [
            ('airflow', self.start_airflow),
            ('data_simulator', self.start_data_simulator),
            ('dashboard', self.start_dashboard)
        ]
        
        for service_name, start_func in services_to_start:
            if self.config['services'].get(service_name, True):
                self.logger.info(f"Starting {service_name}...")
                if not start_func():
                    self.logger.error(f"Failed to start {service_name}")
                    return False
                time.sleep(5)
                
        self.logger.info("All services started successfully!")
        return True
        
    def stop_all_services(self):
        """Stop all running services"""
        self.logger.info("Stopping all services...")
        
        for service_name, process in self.services.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                self.logger.info(f"Stopped {service_name}")
            except Exception as e:
                self.logger.error(f"Error stopping {service_name}: {e}")
                
        # Kill any remaining processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = str(proc.info['cmdline'])
                if any(service in cmdline for service in ['airflow', 'streamlit', 'data_simulator']):
                    proc.kill()
            except:
                pass
                
        self.logger.info("All services stopped")
        
    def status_report(self):
        """Generate system status report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        services = ['airflow', 'dashboard', 'data_simulator']
        
        for service in services:
            status = self.check_service_running(service)
            report["services"][service] = {
                "status": "running" if status else "stopped",
                "port": self.config.get(f"{service}_port", "N/A")
            }
            
        # System metrics
        report["system"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        return report
        
    def run_interactive(self):
        """Run interactive mode"""
        print("🎯 THE RED MACHINE - Complete Trading System")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Start all services")
            print("2. Stop all services")
            print("3. Check status")
            print("4. Retrain model")
            print("5. Run backtest")
            print("6. Configure settings")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.start_all_services()
                
            elif choice == '2':
                self.stop_all_services()
                
            elif choice == '3':
                report = self.status_report()
                print(json.dumps(report, indent=2))
                
            elif choice == '4':
                self.retrain_model()
                
            elif choice == '5':
                self.run_backtest()
                
            elif choice == '6':
                self.configure_interactive()
                
            elif choice == '7':
                self.stop_all_services()
                break
                
            else:
                print("Invalid choice. Please try again.")
                
    def configure_interactive(self):
        """Interactive configuration"""
        print("\nConfiguration:")
        print(f"Current capital: Rs.{self.config['capital']}")
        print(f"Paper trading: {self.config['paper_trading']}")
        print(f"Airflow port: {self.config['airflow_port']}")
        print(f"Dashboard port: {self.config['dashboard_port']}")
        
        # Update configuration
        new_capital = input(f"Enter capital (current: {self.config['capital']}): ").strip()
        if new_capital and new_capital.isdigit():
            self.config['capital'] = int(new_capital)
            
        new_api_key = input("Enter Kite API key (or press Enter to skip): ").strip()
        if new_api_key:
            self.config['kite_api_key'] = new_api_key
            
        new_access_token = input("Enter Kite access token (or press Enter to skip): ").strip()
        if new_access_token:
            self.config['kite_access_token'] = new_access_token
            
        self.save_config()
        print("Configuration updated!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="THE RED MACHINE - Complete Trading System")
    parser.add_argument('--mode', choices=['start', 'stop', 'status', 'interactive'], 
                       default='interactive', help='Operation mode')
    parser.add_argument('--wait-market', action='store_true', 
                       help='Wait for market to open')
    parser.add_argument('--config', type=str, help='Configuration file path')
    
    args = parser.parse_args()
    
    system = CompleteTradingSystem()
    
    if args.config:
        system.config_file = Path(args.config)
        system.load_config()
    
    try:
        if args.mode == 'start':
            if args.wait_market:
                system.wait_for_market_open()
            system.start_all_services()
            
        elif args.mode == 'stop':
            system.stop_all_services()
            
        elif args.mode == 'status':
            report = system.status_report()
            print(json.dumps(report, indent=2))
            
        elif args.mode == 'interactive':
            system.run_interactive()
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        system.stop_all_services()
        
if __name__ == "__main__":
    main()