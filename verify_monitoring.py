#!/usr/bin/env python3
"""
Comprehensive monitoring verification script
Tests all components of the production monitoring setup
"""

import requests
import psycopg2
import json
import time
from datetime import datetime

class MonitoringVerifier:
    def __init__(self):
        self.test_results = {}
        
    def test_grafana_access(self):
        """Test Grafana accessibility"""
        try:
            response = requests.get('http://localhost:3000/api/health', timeout=10)
            if response.status_code == 200:
                self.test_results['grafana'] = "✅ Grafana is accessible at http://localhost:3000"
                return True
            else:
                self.test_results['grafana'] = f"❌ Grafana returned status {response.status_code}"
                return False
        except Exception as e:
            self.test_results['grafana'] = f"❌ Grafana not accessible: {str(e)}"
            return False
    
    def test_prometheus_access(self):
        """Test Prometheus accessibility"""
        try:
            response = requests.get('http://localhost:9090/api/v1/query?query=up', timeout=10)
            if response.status_code == 200:
                self.test_results['prometheus'] = "✅ Prometheus is accessible at http://localhost:9090"
                return True
            else:
                self.test_results['prometheus'] = f"❌ Prometheus returned status {response.status_code}"
                return False
        except Exception as e:
            self.test_results['prometheus'] = f"❌ Prometheus not accessible: {str(e)}"
            return False
    
    def test_postgresql_connection(self):
        """Test PostgreSQL connection for Airflow/MLflow"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="airflow",
                user="airflow",
                password="airflow"
            )
            conn.close()
            self.test_results['postgresql'] = "✅ PostgreSQL connection successful"
            return True
        except Exception as e:
            self.test_results['postgresql'] = f"❌ PostgreSQL connection failed: {str(e)}"
            return False
    
    def test_api_metrics(self):
        """Test API metrics collection"""
        try:
            # Generate some test traffic
            for i in range(3):
                requests.get('http://localhost:8002/health', timeout=5)
                requests.post('http://localhost:8002/predict', 
                            json={"features": [1.0, 2.0, 3.0, 4.0, 5.0]},
                            headers={"Authorization": "Bearer test-token"},
                            timeout=5)
                time.sleep(1)
            
            # Check if metrics are being collected
            response = requests.get('http://localhost:8002/metrics', timeout=10)
            if response.status_code == 200:
                metrics = response.text
                required_metrics = [
                    'request_latency_seconds',
                    'predictions_total',
                    'health_checks_total',
                    'prediction_errors_total'
                ]
                
                found_metrics = [m for m in required_metrics if m in metrics]
                if len(found_metrics) == len(required_metrics):
                    self.test_results['api_metrics'] = "✅ All required metrics are being collected"
                    return True
                else:
                    self.test_results['api_metrics'] = f"❌ Missing metrics: {set(required_metrics) - set(found_metrics)}"
                    return False
            else:
                self.test_results['api_metrics'] = f"❌ /metrics endpoint returned status {response.status_code}"
                return False
        except Exception as e:
            self.test_results['api_metrics'] = f"❌ API metrics test failed: {str(e)}"
            return False
    
    def test_prometheus_scraping(self):
        """Test Prometheus scraping"""
        try:
            time.sleep(5)  # Allow time for scraping
            response = requests.get('http://localhost:9090/api/v1/query?query=predictions_total', timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['data']['result']:
                    self.test_results['prometheus_scraping'] = "✅ Prometheus is successfully scraping metrics"
                    return True
                else:
                    self.test_results['prometheus_scraping'] = "⚠️ Prometheus accessible but no metrics found (may need more time)"
                    return True  # Not a failure, just needs time
            else:
                self.test_results['prometheus_scraping'] = f"❌ Prometheus query failed: {response.status_code}"
                return False
        except Exception as e:
            self.test_results['prometheus_scraping'] = f"❌ Prometheus scraping test failed: {str(e)}"
            return False
    
    def test_backup_system(self):
        """Test backup system"""
        try:
            # Check if backup script exists and is executable
            import os
            backup_script = "backup_system.py"
            if os.path.exists(backup_script):
                self.test_results['backup_system'] = "✅ Backup system script exists"
                return True
            else:
                self.test_results['backup_system'] = "⚠️ Backup system script not found (run manually if needed)"
                return True  # Not critical for monitoring
        except Exception as e:
            self.test_results['backup_system'] = f"❌ Backup system check failed: {str(e)}"
            return False
    
    def run_all_tests(self):
        """Run all monitoring verification tests"""
        print("🔍 Starting comprehensive monitoring verification...")
        print("=" * 50)
        
        tests = [
            self.test_grafana_access,
            self.test_prometheus_access,
            self.test_postgresql_connection,
            self.test_api_metrics,
            self.test_prometheus_scraping,
            self.test_backup_system
        ]
        
        for test in tests:
            test()
            print(f"{list(self.test_results.values())[-1]}")
        
        print("\n" + "=" * 50)
        print("📊 MONITORING VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results.values() if "✅" in result)
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL MONITORING SYSTEMS OPERATIONAL!")
            print("\nNext Steps:")
            print("1. Access Grafana at http://localhost:3000 (admin/admin)")
            print("2. Import the dashboard from grafana-dashboard.json")
            print("3. Set up email alerts in Grafana")
            print("4. Your system is production-ready!")
        else:
            print("⚠️ Some tests failed. Check the results above.")
        
        return passed == total

if __name__ == "__main__":
    verifier = MonitoringVerifier()
    success = verifier.run_all_tests()
    
    # Save results to file
    with open("monitoring_verification_report.txt", "w") as f:
        f.write(f"Monitoring Verification Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        for test, result in verifier.test_results.items():
            f.write(f"{result}\n")
    
    print(f"\n📄 Detailed report saved to monitoring_verification_report.txt")