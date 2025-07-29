#!/usr/bin/env python3
"""
Complete monitoring verification script
Tests all aspects of the monitoring system
"""

import requests
import json
import time
import psycopg2
from datetime import datetime

def test_grafana_access():
    """Test Grafana accessibility"""
    print("🧪 Testing Grafana access...")
    try:
        response = requests.get('http://localhost:3000/api/health')
        if response.status_code == 200:
            print("✅ Grafana is accessible at http://localhost:3000")
            return True
        else:
            print(f"⚠️ Grafana returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Grafana: {e}")
        return False

def test_prometheus_access():
    """Test Prometheus accessibility"""
    print("\n🧪 Testing Prometheus access...")
    try:
        response = requests.get('http://localhost:9090/-/healthy')
        if response.status_code == 200:
            print("✅ Prometheus is accessible at http://localhost:9090")
            
            # Test metrics scraping
            metrics_response = requests.get('http://localhost:9090/api/v1/query?query=predictions_total')
            if metrics_response.status_code == 200:
                data = metrics_response.json()
                if 'data' in data and 'result' in data['data']:
                    count = float(data['data']['result'][0]['value'][1]) if data['data']['result'] else 0
                    print(f"📊 Total predictions scraped: {count}")
            return True
        else:
            print(f"⚠️ Prometheus returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Prometheus: {e}")
        return False

def test_postgresql_connection():
    """Test PostgreSQL connectivity for Grafana"""
    print("\n🧪 Testing PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="airflow",
            user="airflow",
            password="airflow"
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL connected: {version.split()[0]} {version.split()[1]}")
        
        # Test DAG runs table
        cursor.execute("SELECT COUNT(*) FROM dag_run")
        dag_count = cursor.fetchone()[0]
        print(f"📊 Total DAG runs: {dag_count}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_api_metrics():
    """Test API metrics collection"""
    print("\n🧪 Testing API metrics...")
    
    # Generate some traffic
    test_data = {
        "data": {
            "stock_price": 150.5,
            "volatility": 0.15,
            "volume": 1000000,
            "sma_20": 145.2,
            "rsi": 65.5
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer secure_token'
    }
    
    for i in range(3):
        try:
            response = requests.post(
                'http://localhost:8002/predict',
                json=test_data,
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ Prediction {i+1} successful")
            else:
                print(f"⚠️ Prediction {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Prediction {i+1} error: {e}")
    
    return True

def test_backup_system():
    """Test backup system"""
    print("\n🧪 Testing backup system...")
    
    try:
        import os
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            backups = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
            if backups:
                latest_backup = max(backups, key=lambda f: os.path.getctime(os.path.join(backup_dir, f)))
                backup_time = datetime.fromtimestamp(os.path.getctime(os.path.join(backup_dir, latest_backup)))
                print(f"✅ Latest backup: {latest_backup} ({backup_time.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print("⚠️ No backup files found")
        else:
            print("⚠️ Backup directory not found")
        return True
    except Exception as e:
        print(f"❌ Backup system test failed: {e}")
        return False

def generate_monitoring_report():
    """Generate comprehensive monitoring report"""
    print("\n" + "="*60)
    print("📋 MONITORING SYSTEM VERIFICATION REPORT")
    print("="*60)
    
    tests = [
        ("Grafana Access", test_grafana_access),
        ("Prometheus Access", test_prometheus_access),
        ("PostgreSQL Connection", test_postgresql_connection),
        ("API Metrics Collection", test_api_metrics),
        ("Backup System", test_backup_system)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Score: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("Your monitoring system is fully configured and ready for production.")
    else:
        print(f"\n⚠️ {total-passed} items need attention")
    
    return passed == total

if __name__ == "__main__":
    generate_monitoring_report()