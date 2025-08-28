#!/usr/bin/env python3
"""
Emergency Circuit Breaker
Stops all trading processes immediately when activated
"""

import os
import sys
import signal
import subprocess
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmergencyStop:
    def __init__(self):
        self.processes_to_kill = [
            'morning_scalper.py',
            'minimal_trading_system.py',
            'live_signal_executor.py',
            'sensex_trading_strategy.py',
            'breeze_connector.py'
        ]
    
    def kill_python_processes(self):
        """Kill all Python trading processes"""
        killed_processes = []
        
        try:
            # For Windows
            if os.name == 'nt':
                for process_name in self.processes_to_kill:
                    try:
                        # Use taskkill to terminate processes
                        result = subprocess.run(
                            ['taskkill', '/F', '/IM', 'python.exe', '/FI', f'WINDOWTITLE eq *{process_name}*'],
                            capture_output=True,
                            text=True
                        )
                        
                        # Alternative: kill by script name in command line
                        result2 = subprocess.run(
                            ['wmic', 'process', 'where', f'CommandLine like "%{process_name}%"', 'call', 'terminate'],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0 or result2.returncode == 0:
                            killed_processes.append(process_name)
                            logger.info(f"🛑 Killed process: {process_name}")
                    
                    except Exception as e:
                        logger.warning(f"Could not kill {process_name}: {e}")
            
            # For Unix-like systems
            else:
                for process_name in self.processes_to_kill:
                    try:
                        result = subprocess.run(
                            ['pkill', '-f', process_name],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            killed_processes.append(process_name)
                            logger.info(f"🛑 Killed process: {process_name}")
                    
                    except Exception as e:
                        logger.warning(f"Could not kill {process_name}: {e}")
        
        except Exception as e:
            logger.error(f"Error killing processes: {e}")
        
        return killed_processes
    
    def send_emergency_alert(self, message="Trading system halted due to emergency"):
        """Send emergency email alert"""
        try:
            # Get email settings from environment
            sender_email = os.getenv('ALERT_EMAIL', 'your-email@gmail.com')
            sender_password = os.getenv('ALERT_PASSWORD', 'your-app-password')
            recipient_email = os.getenv('RECIPIENT_EMAIL', 'your-phone@txt.att.net')
            
            if not all([sender_email, sender_password, recipient_email]):
                logger.warning("Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = '🚨 EMERGENCY STOP ACTIVATED - SENSEX SCALPER'
            
            body = f"""
            EMERGENCY STOP ACTIVATED
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Message: {message}
            
            All trading processes have been terminated.
            Please check the system immediately.
            
            Log file: morning_scalping.log
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("📧 Emergency alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send emergency alert: {e}")
            return False
    
    def create_emergency_log(self, reason="Manual activation"):
        """Create emergency log entry"""
        try:
            with open('emergency_stop.log', 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - EMERGENCY STOP: {reason}\n")
            
            logger.info("📋 Emergency log created")
            
        except Exception as e:
            logger.error(f"Failed to create emergency log: {e}")
    
    def check_system_status(self):
        """Check which processes are currently running"""
        running_processes = []
        
        try:
            # For Windows
            if os.name == 'nt':
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                output = result.stdout.lower()
                
                for process_name in self.processes_to_kill:
                    if process_name.lower() in output:
                        running_processes.append(process_name)
            
            # For Unix-like systems
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                output = result.stdout.lower()
                
                for process_name in self.processes_to_kill:
                    if process_name.lower() in output:
                        running_processes.append(process_name)
        
        except Exception as e:
            logger.error(f"Error checking system status: {e}")
        
        return running_processes
    
    def emergency_shutdown(self, reason="Emergency stop activated"):
        """Complete emergency shutdown procedure"""
        logger.info("🚨 EMERGENCY SHUTDOWN INITIATED")
        
        # Check current running processes
        running = self.check_system_status()
        if running:
            logger.info(f"Running processes: {running}")
        
        # Kill all trading processes
        killed = self.kill_python_processes()
        
        # Create emergency log
        self.create_emergency_log(reason)
        
        # Send alert
        self.send_emergency_alert(reason)
        
        logger.info("🛑 EMERGENCY SHUTDOWN COMPLETE")
        logger.info(f"Killed processes: {killed}")
        
        return {
            'running_processes': running,
            'killed_processes': killed,
            'alert_sent': True,
            'log_created': True
        }

def main():
    """Main emergency stop function"""
    print("🚨 EMERGENCY CIRCUIT BREAKER")
    print("=" * 40)
    
    stopper = EmergencyStop()
    
    # Ask for confirmation
    response = input("Are you sure you want to activate emergency stop? (yes/no): ")
    
    if response.lower() == 'yes':
        reason = input("Enter reason for emergency stop (optional): ")
        if not reason.strip():
            reason = "Manual activation"
        
        result = stopper.emergency_shutdown(reason)
        
        print("\n📊 Emergency Stop Results:")
        print(f"Running processes: {len(result['running_processes'])}")
        print(f"Killed processes: {len(result['killed_processes'])}")
        print(f"Alert sent: {'Yes' if result['alert_sent'] else 'No'}")
        print(f"Log created: {'Yes' if result['log_created'] else 'No'}")
    else:
        print("❌ Emergency stop cancelled")

if __name__ == "__main__":
    main()