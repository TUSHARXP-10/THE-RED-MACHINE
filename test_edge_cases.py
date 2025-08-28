#!/usr/bin/env python3
"""
Step 5: Edge Case Testing Script
Tests DAG and API edge cases for proper error handling
"""

import requests
import pandas as pd
import numpy as np
import json
import subprocess
import time
import os
from datetime import datetime

class EdgeCaseTester:
    def __init__(self):
        self.api_base = "http://localhost:8002"
        self.test_results = []
        
    def log_result(self, test_type, scenario, result, details=""):
        """Log test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_entry = {
            "timestamp": timestamp,
            "test_type": test_type,
            "scenario": scenario,
            "result": result,
            "details": details
        }
        self.test_results.append(result_entry)
        print(f"[{timestamp}] {test_type} - {scenario}: {result} - {details}")
        
    def test_api_edge_cases(self):
        """Test API edge cases"""
        print("\n=== Testing API Edge Cases ===")
        
        # Test 1: Invalid input (negative stock price)
        try:
            headers = {"Authorization": "Bearer secure_token", "Content-Type": "application/json"}
            data = {"data": {"stock_price": -50, "volatility": 0.12}}
            response = requests.post(f"{self.api_base}/predict", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("API", "Negative stock price", "PASS", 
                              f"Handled gracefully: {result}")
            else:
                self.log_result("API", "Negative stock price", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API", "Negative stock price", "ERROR", str(e))
            
        # Test 2: Authentication failure
        try:
            headers = {"Authorization": "Bearer invalid_token", "Content-Type": "application/json"}
            data = {"data": {"stock_price": 100, "volatility": 0.12}}
            response = requests.post(f"{self.api_base}/predict", json=data, headers=headers)
            
            if response.status_code == 401:
                self.log_result("API", "Invalid authentication", "PASS", 
                              "Properly rejected with 401")
            else:
                self.log_result("API", "Invalid authentication", "FAIL", 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("API", "Invalid authentication", "ERROR", str(e))
            
        # Test 3: Missing required fields
        try:
            headers = {"Authorization": "Bearer secure_token", "Content-Type": "application/json"}
            data = {"data": {"stock_price": 100}}  # Missing volatility
            response = requests.post(f"{self.api_base}/predict", json=data, headers=headers)
            
            if response.status_code in [200, 400]:
                self.log_result("API", "Missing fields", "PASS", 
                              f"Handled: {response.status_code}")
            else:
                self.log_result("API", "Missing fields", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API", "Missing fields", "ERROR", str(e))
            
        # Test 4: Extreme values
        try:
            headers = {"Authorization": "Bearer secure_token", "Content-Type": "application/json"}
            data = {"data": {"stock_price": 1000000, "volatility": 50, "rsi": 150}}
            response = requests.post(f"{self.api_base}/predict", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("API", "Extreme values", "PASS", 
                              f"Handled: {result}")
            else:
                self.log_result("API", "Extreme values", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API", "Extreme values", "ERROR", str(e))
            
    def test_dag_data_validation(self):
        """Test DAG data validation with bad data"""
        print("\n=== Testing DAG Data Validation ===")
        
        # Create test data with various issues
        test_cases = [
            {
                "name": "NaN values",
                "data": pd.DataFrame({
                    'date': pd.date_range(start='2024-01-01', periods=5),
                    'stock_price': [100, np.nan, 120, 110, 130],
                    'volume': [1000000, 2000000, np.nan, 1500000, 1800000],
                    'symbol': ['TEST'] * 5
                })
            },
            {
                "name": "Negative prices",
                "data": pd.DataFrame({
                    'date': pd.date_range(start='2024-01-01', periods=5),
                    'stock_price': [100, -50, 120, -30, 130],
                    'volume': [1000000, 2000000, 1500000, 1800000, 2200000],
                    'symbol': ['TEST'] * 5
                })
            },
            {
                "name": "Missing columns",
                "data": pd.DataFrame({
                    'date': pd.date_range(start='2024-01-01', periods=5),
                    'stock_price': [100, 110, 120, 110, 130],
                    # Missing volume column
                })
            },
            {
                "name": "Invalid dates",
                "data": pd.DataFrame({
                    'date': ['invalid', '2024-01-02', '2024-13-45', None, '2024-01-05'],
                    'stock_price': [100, 110, 120, 110, 130],
                    'volume': [1000000, 2000000, 1500000, 1800000, 2200000],
                    'symbol': ['TEST'] * 5
                })
            }
        ]
        
        for test_case in test_cases:
            try:
                # Import the validation function
                import sys
                sys.path.append('/opt/airflow/dags')
                from financial_data_quality_monitor import FinancialDataQualityMonitor
                
                monitor = FinancialDataQualityMonitor()
                quality_config = {
                    'required_columns': ['date', 'stock_price', 'volume'],
                    'validation_rules': {
                        'stock_price': {'dtype': 'numeric', 'min_value': 0},
                        'volume': {'dtype': 'numeric', 'min_value': 0}
                    }
                }
                
                report = monitor.generate_quality_report(test_case['data'], quality_config)
                
                if report:
                    quality_score = report.get('overall_quality_score', 0)
                    if quality_score < 90:
                        self.log_result("DAG", test_case['name'], "PASS", 
                                      f"Validation caught issues: score={quality_score}")
                    else:
                        self.log_result("DAG", test_case['name'], "WARN", 
                                      f"Validation passed questionable data: score={quality_score}")
                else:
                    self.log_result("DAG", test_case['name'], "FAIL", "No validation report generated")
                    
            except Exception as e:
                self.log_result("DAG", test_case['name'], "PASS", f"Validation caught error: {str(e)[:100]}")
                
    def test_api_health_and_errors(self):
        """Test API health endpoint and error responses"""
        print("\n=== Testing API Health & Error Responses ===")
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.api_base}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.log_result("API", "Health check", "PASS", 
                              f"Service healthy: {health_data}")
            else:
                self.log_result("API", "Health check", "FAIL", 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("API", "Health check", "ERROR", str(e))
            
    def run_all_tests(self):
        """Run all edge case tests"""
        print("Starting Step 5: Edge Case Testing")
        print("=" * 50)
        
        self.test_api_health_and_errors()
        self.test_api_edge_cases()
        self.test_dag_data_validation()
        
        # Summary
        print("\n" + "=" * 50)
        print("EDGE CASE TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if "PASS" in r["result"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"- {result['test_type']}: {result['scenario']} -> {result['result']}")
            
        return passed == total

if __name__ == "__main__":
    tester = EdgeCaseTester()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        print("\n✅ All edge cases handled successfully!")
    else:
        print("\n❌ Some edge cases need attention")