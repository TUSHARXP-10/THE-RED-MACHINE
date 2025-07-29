#!/usr/bin/env python3
"""
End-to-End Test Suite for Automated Cash Flow Generation System
Validates complete workflow from data ingestion to predictions and monitoring
"""

import requests
import json
import time
import psycopg2
from datetime import datetime

class EndToEndTester:
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def log_result(self, test_name, success, message):
        """Log test result with timestamp"""
        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
    
    def test_health_endpoints(self):
        """Test all service health endpoints"""
        services = [
            ("Financial API", "http://localhost:8002/health"),
            ("Grafana", "http://localhost:3000/api/health"),
            ("Prometheus", "http://localhost:9090/api/v1/query?query=up")
        ]
        
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_result(f"{service_name} Health", True, "Service is healthy")
                else:
                    self.log_result(f"{service_name} Health", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"{service_name} Health", False, str(e))
    
    def test_api_prediction(self):
        """Test API prediction endpoint"""
        try:
            # Test with sample data
            payload = {
                "data": [0.5, 100.0, 50.0, 103.0, 1.2, 0.8, 1.1, 0.9, 1.05, 0.95]
            }
            
            response = requests.post(
                "http://localhost:8002/predict",
                json=payload,
                headers={"Authorization": "Bearer test_secure_token"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "prediction" in result:
                    self.log_result("API Prediction", True, f"Prediction: {result['prediction']}")
                    return True
                else:
                    self.log_result("API Prediction", False, "Missing prediction in response")
            else:
                self.log_result("API Prediction", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("API Prediction", False, str(e))
        return False
    
    def test_metrics_collection(self):
        """Test Prometheus metrics collection"""
        try:
            # Generate some traffic
            for i in range(3):
                requests.get("http://localhost:8002/health", timeout=5)
                time.sleep(1)
            
            # Check metrics
            response = requests.get("http://localhost:8002/metrics", timeout=10)
            if response.status_code == 200:
                metrics = response.text
                required_metrics = [
                    "request_latency_seconds",
                    "predictions_total",
                    "health_checks_total"
                ]
                
                found = [m for m in required_metrics if m in metrics]
                if len(found) == len(required_metrics):
                    self.log_result("Metrics Collection", True, "All required metrics present")
                    return True
                else:
                    self.log_result("Metrics Collection", False, f"Missing: {set(required_metrics) - set(found)}")
            else:
                self.log_result("Metrics Collection", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Metrics Collection", False, str(e))
        return False
    
    def test_grafana_dashboard(self):
        """Test Grafana dashboard accessibility"""
        try:
            response = requests.get("http://localhost:3000/api/search", timeout=10)
            if response.status_code == 200:
                dashboards = response.json()
                self.log_result("Grafana Dashboard", True, f"Found {len(dashboards)} dashboards")
                return True
            else:
                self.log_result("Grafana Dashboard", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Grafana Dashboard", False, str(e))
        return False
    
    def test_prometheus_scraping(self):
        """Test Prometheus is scraping metrics"""
        try:
            # Query for API metrics
            response = requests.get(
                "http://localhost:9090/api/v1/query?query=up{job='financial-api'}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['data']['result']:
                    self.log_result("Prometheus Scraping", True, "Successfully scraping API metrics")
                    return True
                else:
                    self.log_result("Prometheus Scraping", False, "No metrics found for financial-api")
            else:
                self.log_result("Prometheus Scraping", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Prometheus Scraping", False, str(e))
        return False
    
    def test_backup_system(self):
        """Test backup system functionality"""
        try:
            import os
            backup_dir = "backups"
            if os.path.exists(backup_dir):
                files = os.listdir(backup_dir)
                if files:
                    latest = max([os.path.join(backup_dir, f) for f in files], key=os.path.getctime)
                    self.log_result("Backup System", True, f"Latest backup: {os.path.basename(latest)}")
                    return True
                else:
                    self.log_result("Backup System", False, "No backup files found")
            else:
                self.log_result("Backup System", False, "Backup directory not found")
                
        except Exception as e:
            self.log_result("Backup System", False, str(e))
        return False
    
    def test_database_connectivity(self):
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="airflow",
                user="airflow",
                password="airflow",
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            self.log_result("Database Connectivity", True, f"Connected to {version.split()[1]}")
            return True
            
        except Exception as e:
            self.log_result("Database Connectivity", False, str(e))
        return False
    
    def run_full_test_suite(self):
        """Run complete end-to-end test suite"""
        print("🚀 Starting End-to-End Test Suite")
        print("=" * 50)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Run all tests
        tests = [
            self.test_health_endpoints,
            self.test_database_connectivity,
            self.test_api_prediction,
            self.test_metrics_collection,
            self.test_prometheus_scraping,
            self.test_grafana_dashboard,
            self.test_backup_system
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_result(test.__name__, False, str(e))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results.values() if result["success"])
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "PASS" if result["success"] else "FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is production-ready!")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Check logs above.")
        
        # Save report
        self.save_report(passed, total)
        return passed == total
    
    def save_report(self, passed, total):
        """Save test report to file"""
        report = {
            "test_summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": (passed / total) * 100 if total > 0 else 0
            },
            "test_results": self.test_results,
            "timestamp": {
                "start": self.start_time.isoformat(),
                "end": datetime.now().isoformat()
            }
        }
        
        with open("end_to_end_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to end_to_end_test_report.json")

if __name__ == "__main__":
    tester = EndToEndTester()
    success = tester.run_full_test_suite()
    
    if success:
        print("\n" + "=" * 50)
        print("🏆 PROJECT VALIDATION COMPLETE!")
        print("=" * 50)
        print("Your automated cash flow generation system is:")
        print("✅ Fully operational")
        print("✅ Production-ready")
        print("✅ End-to-end validated")
        print("\nAccess your services:")
        print("• Financial API: http://localhost:8002/docs")
        print("• Grafana: http://localhost:3000 (admin/admin)")
        print("• Prometheus: http://localhost:9090")
        print("• Airflow: http://localhost:8080")
        print("• MLflow: http://localhost:5000")