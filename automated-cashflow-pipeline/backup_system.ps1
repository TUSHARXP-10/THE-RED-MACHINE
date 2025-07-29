# backup_system.ps1 - Automated Backup Script

# Configuration
$BACKUP_DIR = "C:\Users\tushar\Desktop\THE-RED MACHINE\automated-cashflow-pipeline\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmm"
$RETENTION_DAYS = 7
$EMAIL_FROM = "your.email@example.com"
$EMAIL_TO = "alert@example.com"
$SMTP_SERVER = "smtp.example.com"
$SMTP_PORT = 587
$SMTP_USER = "your.email@example.com"
$SMTP_PASS = "your_password"

# Function to send email alert
function Send-Alert {
    param ([string]$Subject, [string]$Body)
    $securePass = ConvertTo-SecureString $SMTP_PASS -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ($SMTP_USER, $securePass)
    
    Send-MailMessage -From $EMAIL_FROM -To $EMAIL_TO -Subject $Subject -Body $Body `
                     -SmtpServer $SMTP_SERVER -Port $SMTP_PORT -UseSsl -Credential $cred
}

try {
    # Change to the correct directory for docker-compose and relative paths
    Set-Location -Path "C:\Users\tushar\Desktop\THE-RED MACHINE\automated-cashflow-pipeline"

    # 1. Backup PostgreSQL Database
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U airflow airflow > "$BACKUP_DIR/airflow_db_$TIMESTAMP.sql"

    # 2. Backup MLflow Artifacts
    if (Test-Path "./mlruns") {
        Copy-Item -Path "./mlruns" -Destination "$BACKUP_DIR/mlruns_$TIMESTAMP" -Recurse
    } else {
        Write-Warning "MLflow artifacts directory './mlruns' not found. Skipping backup."
    }

    # 3. Backup Models Directory
    if (Test-Path "./models") {
        Copy-Item -Path "./models" -Destination "$BACKUP_DIR/models_$TIMESTAMP" -Recurse
    } else {
        Write-Warning "Models directory './models' not found. Skipping backup."
    }

    # 4. Backup Warehouse Data
    if (Test-Path "./data/warehouse") {
        Copy-Item -Path "./data/warehouse" -Destination "$BACKUP_DIR/warehouse_$TIMESTAMP" -Recurse
    } else {
        Write-Warning "Warehouse data directory './data/warehouse' not found. Skipping backup."
    }

    # Cleanup old backups
    Get-ChildItem $BACKUP_DIR -Recurse -File | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-$RETENTION_DAYS) } | Remove-Item -Force

    # Log success
    Write-Output "Backup completed successfully at $TIMESTAMP" | Out-File -FilePath "$BACKUP_DIR/backup_log.txt" -Append

} catch {
    $errorMsg = $_.Exception.Message
    Write-Output "Backup failed at ${TIMESTAMP}: ${errorMsg}" | Out-File -FilePath "${BACKUP_DIR}/backup_log.txt" -Append
    Send-Alert -Subject "Backup Failed" -Body "Error: $errorMsg at $TIMESTAMP"
}