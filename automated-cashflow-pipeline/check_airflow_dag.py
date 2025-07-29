#!/usr/bin/env python3
"""
Script to check Airflow DAG status and trigger the financial_pipeline DAG
"""
import requests
import json
import time
from requests.auth import HTTPBasicAuth

def check_airflow_dag():
    """Check Airflow DAG status and trigger if needed"""
    
    # Airflow configuration
    airflow_url = "http://localhost:8080"
    username = "admin"
    password = "admin"
    
    print("🔍 Checking Airflow DAG status...")
    
    try:
        # First, let's check if we can access the API
        auth = HTTPBasicAuth(username, password)
        
        # Check available DAGs
        dags_url = f"{airflow_url}/api/v1/dags"
        response = requests.get(dags_url, auth=auth)
        
        if response.status_code == 200:
            dags = response.json()
            print(f"✅ Successfully connected to Airflow")
            
            # Look for financial related DAGs
            financial_dags = []
            for dag in dags.get('dags', []):
                if 'financial' in dag['dag_id'].lower():
                    financial_dags.append(dag)
            
            if financial_dags:
                print(f"📊 Found {len(financial_dags)} financial DAG(s):")
                for dag in financial_dags:
                    dag_id = dag['dag_id']
                    is_paused = dag['is_paused']
                    
                    print(f"   • {dag_id} - {'Paused' if is_paused else 'Active'}")
                    
                    # Check specific DAG details
                    dag_url = f"{airflow_url}/api/v1/dags/{dag_id}"
                    dag_response = requests.get(dag_url, auth=auth)
                    
                    if dag_response.status_code == 200:
                        dag_details = dag_response.json()
                        print(f"     Description: {dag_details.get('description', 'No description')}")
                        
                        # Check recent runs
                        runs_url = f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns?limit=5"
                        runs_response = requests.get(runs_url, auth=auth)
                        
                        if runs_response.status_code == 200:
                            runs = runs_response.json()
                            if runs.get('dag_runs'):
                                latest_run = runs['dag_runs'][0]
                                print(f"     Latest run: {latest_run['state']} ({latest_run['start_date']})")
                            else:
                                print("     No runs found")
                        
                        # If DAG is paused, unpause it
                        if is_paused:
                            print(f"     🔄 Unpausing DAG {dag_id}...")
                            patch_data = {"is_paused": False}
                            patch_response = requests.patch(
                                dag_url,
                                auth=auth,
                                headers={'Content-Type': 'application/json'},
                                json=patch_data
                            )
                            
                            if patch_response.status_code == 200:
                                print(f"     ✅ DAG {dag_id} unpaused successfully")
                            else:
                                print(f"     ❌ Failed to unpause DAG: {patch_response.status_code}")
                        
                        # Trigger the DAG
                        print(f"     🚀 Triggering DAG {dag_id}...")
                        trigger_url = f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns"
                        trigger_data = {"conf": {}}
                        
                        trigger_response = requests.post(
                            trigger_url,
                            auth=auth,
                            headers={'Content-Type': 'application/json'},
                            json=trigger_data
                        )
                        
                        if trigger_response.status_code == 200:
                            new_run = trigger_response.json()
                            print(f"     ✅ DAG triggered successfully! Run ID: {new_run['dag_run_id']}")
                            
                            # Monitor the run
                            print("     ⏳ Monitoring run progress...")
                            for i in range(10):  # Monitor for up to 50 seconds
                                time.sleep(5)
                                run_status_url = f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns/{new_run['dag_run_id']}"
                                status_response = requests.get(run_status_url, auth=auth)
                                
                                if status_response.status_code == 200:
                                    run_status = status_response.json()
                                    state = run_status['state']
                                    print(f"     📊 Run state: {state}")
                                    
                                    if state in ['success', 'failed']:
                                        print(f"     🎯 Run completed with state: {state}")
                                        return state == 'success'
                                else:
                                    print(f"     ❌ Failed to check run status: {status_response.status_code}")
                            
                            print("     ⚠️  Run monitoring timed out")
                            return False
                        else:
                            print(f"     ❌ Failed to trigger DAG: {trigger_response.status_code}")
                            print(f"     Response: {trigger_response.text}")
                    else:
                        print(f"     ❌ Failed to get DAG details: {dag_response.status_code}")
            else:
                print("❌ No financial DAGs found")
                return False
                
        else:
            print(f"❌ Failed to connect to Airflow API: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing Airflow: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_airflow_dag()
    if success:
        print("\n🎉 Airflow DAG test completed successfully!")
    else:
        print("\n⚠️  Airflow DAG test encountered issues")