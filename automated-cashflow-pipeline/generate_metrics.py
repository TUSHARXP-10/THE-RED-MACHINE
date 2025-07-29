#!/usr/bin/env python3
"""
Generate sample metrics for Grafana dashboards
This script creates sample data in the format expected by the monitoring setup
"""

import psycopg2
import json
import random
import time
from datetime import datetime, timedelta
import os

def create_metrics_tables():
    """Create tables for storing metrics if they don't exist"""
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cursor = conn.cursor()
    
    # Create metrics tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_health_logs (
            id SERIAL PRIMARY KEY,
            status_code INTEGER,
            response_time_ms FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_performance_logs (
            id SERIAL PRIMARY KEY,
            endpoint VARCHAR(100),
            response_time_ms FLOAT,
            status_code INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id SERIAL PRIMARY KEY,
            prediction_value FLOAT,
            features JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_access_logs (
            id SERIAL PRIMARY KEY,
            endpoint VARCHAR(100),
            method VARCHAR(10),
            status_code INTEGER,
            response_time_ms FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Metrics tables created successfully")

def generate_sample_data():
    """Generate sample metrics data for the last 24 hours"""
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cursor = conn.cursor()
    
    # Generate 24 hours of data
    base_time = datetime.now() - timedelta(hours=24)
    
    # API health logs (every 5 minutes)
    for i in range(288):  # 24 * 12 (5-minute intervals)
        timestamp = base_time + timedelta(minutes=i*5)
        status_code = 200 if random.random() > 0.05 else 500  # 95% uptime
        response_time = random.uniform(50, 200)  # 50-200ms
        
        cursor.execute(
            "INSERT INTO api_health_logs (status_code, response_time_ms, timestamp) VALUES (%s, %s, %s)",
            (status_code, response_time, timestamp)
        )
    
    # API performance logs
    endpoints = ['/health', '/predict', '/metrics']
    for i in range(500):  # 500 requests over 24 hours
        timestamp = base_time + timedelta(hours=random.uniform(0, 24))
        endpoint = random.choice(endpoints)
        response_time = random.uniform(50, 500)
        status_code = 200 if random.random() > 0.1 else random.choice([400, 404, 500])
        
        cursor.execute(
            "INSERT INTO api_performance_logs (endpoint, response_time_ms, status_code, timestamp) VALUES (%s, %s, %s, %s)",
            (endpoint, response_time, status_code, timestamp)
        )
    
    # Prediction logs
    for i in range(100):  # 100 predictions
        timestamp = base_time + timedelta(hours=random.uniform(0, 24))
        prediction_value = random.uniform(90, 110)
        features = json.dumps([random.uniform(0, 100) for _ in range(5)])
        
        cursor.execute(
            "INSERT INTO prediction_logs (prediction_value, features, timestamp) VALUES (%s, %s, %s)",
            (prediction_value, features, timestamp)
        )
    
    # API access logs
    methods = ['GET', 'POST']
    for i in range(1000):  # 1000 API calls
        timestamp = base_time + timedelta(hours=random.uniform(0, 24))
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        response_time = random.uniform(30, 400)
        status_code = 200 if random.random() > 0.08 else random.choice([400, 401, 404, 500])
        
        cursor.execute(
            "INSERT INTO api_access_logs (endpoint, method, status_code, response_time_ms, timestamp) VALUES (%s, %s, %s, %s, %s)",
            (endpoint, method, status_code, response_time, timestamp)
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Sample metrics data generated successfully")

def test_grafana_connection():
    """Test if Grafana is accessible"""
    import requests
    try:
        response = requests.get('http://localhost:3000/api/health', timeout=5)
        if response.status_code == 200:
            print("✓ Grafana is accessible at http://localhost:3000")
            return True
        else:
            print("⚠ Grafana returned status code:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("⚠ Cannot connect to Grafana:", str(e))
        return False

def main():
    """Main function to set up metrics"""
    print("🚀 Setting up Grafana monitoring metrics...")
    print("=" * 50)
    
    # Test Grafana connection
    test_grafana_connection()
    
    # Create metrics tables
    try:
        create_metrics_tables()
    except Exception as e:
        print("❌ Error creating tables:", str(e))
        return
    
    # Generate sample data
    try:
        generate_sample_data()
        print("✓ Sample data generated for testing dashboards")
    except Exception as e:
        print("❌ Error generating sample data:", str(e))
        return
    
    print("\n📊 Setup complete!")
    print("Next steps:")
    print("1. Open http://localhost:3000")
    print("2. Login with admin/admin")
    print("3. Add PostgreSQL data source (host: localhost:5432)")
    print("4. Create dashboards using the sample data")

if __name__ == "__main__":
    main()