import os
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path

def setup_airflow_local():
    # Create a temporary directory for Airflow
    temp_dir = Path("C:/airflow_workspace")
    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up directories
    airflow_home = temp_dir / "airflow"
    airflow_home.mkdir(exist_ok=True)
    
    dags_dir = airflow_home / "dags"
    dags_dir.mkdir(exist_ok=True)
    
    logs_dir = airflow_home / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Copy existing DAGs
    project_dags = Path("automated-cashflow-pipeline/dags")
    if project_dags.exists():
        for dag_file in project_dags.glob("*.py"):
            shutil.copy2(dag_file, dags_dir)
    
    # Set environment variables with correct SQLite format
    os.environ['AIRFLOW_HOME'] = str(airflow_home)
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = str(dags_dir)
    os.environ['AIRFLOW__CORE__EXECUTOR'] = 'SequentialExecutor'
    os.environ['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'False'
    
    # Use proper SQLite URL format with four slashes
    db_path = airflow_home / "airflow.db"
    os.environ['AIRFLOW__DATABASE__SQL_ALCHEMY_CONN'] = f"sqlite:////{db_path}".replace('\\', '/')
    
    print(f"AIRFLOW_HOME: {airflow_home}")
    print(f"DAGS_FOLDER: {dags_dir}")
    print(f"Database: {db_path}")
    
    # Initialize database
    try:
        subprocess.run([sys.executable, "-m", "airflow", "db", "init"], check=True)
        print("Database initialized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Database initialization failed: {e}")
        return False
    
    # Create admin user
    try:
        subprocess.run([
            sys.executable, "-m", "airflow", "users", "create",
            "--username", "admin",
            "--firstname", "Admin",
            "--lastname", "User",
            "--role", "Admin",
            "--email", "admin@example.com",
            "--password", "admin"
        ], check=True)
        print("Admin user created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"User creation failed: {e}")
        return False
    
    # Start webserver
    print("Starting Airflow webserver...")
    print("Access Airflow at: http://localhost:8080")
    print("Username: admin")
    print("Password: admin")
    
    subprocess.run([
        sys.executable, "-m", "airflow", "webserver",
        "--port", "8080"
    ])

if __name__ == "__main__":
    setup_airflow_local()