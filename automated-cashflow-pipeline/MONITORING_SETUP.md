# Grafana Monitoring Setup Guide

## Overview
This guide will help you set up basic monitoring for your automated cash flow pipeline using Grafana dashboards and alerts.

## Step 1: Access Grafana
- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin
- **Action**: Change the default password when prompted

## Step 2: Add Data Sources

### PostgreSQL Data Source (Airflow Database)
1. Click **Configuration** (gear icon) → **Data Sources**
2. Click **Add data source**
3. Select **PostgreSQL**
4. Configure:
   - **Name**: Airflow PostgreSQL
   - **Host**: postgres:5432
   - **Database**: airflow
   - **User**: airflow
   - **Password**: airflow
   - **SSL Mode**: disable
5. Click **Save & Test**

### Prometheus Data Source (if available)
1. Click **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Configure:
   - **Name**: Docker Metrics
   - **URL**: http://host.docker.internal:9090
   - **Access**: Server
5. Click **Save & Test**

## Step 3: Create Dashboards

### Dashboard 1: System Overview
1. Click **Create** (+) → **Dashboard**
2. Click **Add new panel**

#### Panel 1: API Health Status
- **Query Type**: PostgreSQL
- **Query**:
```sql
SELECT 
  CASE 
    WHEN status_code = 200 THEN 1 
    ELSE 0 
  END as healthy,
  timestamp
FROM api_health_logs
ORDER BY timestamp DESC
LIMIT 100
```
- **Visualization**: Time series
- **Title**: API Health Status

#### Panel 2: DAG Run Status
- **Query Type**: PostgreSQL
- **Query**:
```sql
SELECT 
  state,
  COUNT(*) as count
FROM dag_run
WHERE execution_date >= NOW() - INTERVAL '24 hours'
GROUP BY state
```
- **Visualization**: Pie chart
- **Title**: DAG Run Status (24h)

#### Panel 3: API Response Time
- **Query Type**: PostgreSQL
- **Query**:
```sql
SELECT 
  AVG(response_time_ms) as avg_response_time,
  timestamp
FROM api_performance_logs
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY timestamp
ORDER BY timestamp
```
- **Visualization**: Time series
- **Title**: Average API Response Time (1h)

### Dashboard 2: Financial API Metrics
1. Create new dashboard: **CashFlow API Monitoring**

#### Panel 1: Prediction Volume
- **Query Type**: PostgreSQL
- **Query**:
```sql
SELECT 
  COUNT(*) as prediction_count,
  DATE_TRUNC('hour', timestamp) as hour
FROM prediction_logs
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour
```
- **Visualization**: Bar gauge
- **Title**: Predictions per Hour

#### Panel 2: Error Rate
- **Query Type**: PostgreSQL
- **Query**:
```sql
SELECT 
  SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END)::float / COUNT(*) * 100 as error_rate,
  DATE_TRUNC('hour', timestamp) as hour
FROM api_access_logs
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour
```
- **Visualization**: Time series
- **Title**: API Error Rate (%)

## Step 4: Set Up Alerts

### Alert 1: API Health Check
1. Go to **Alerting** → **Alert Rules**
2. Click **New alert rule**
3. Configure:
   - **Name**: API Health Alert
   - **Query**: Same as API Health panel
   - **Condition**: WHEN last() OF query(A, 5m, now) IS BELOW 1
   - **Evaluate every**: 1m
   - **For**: 0m
4. **Notification**: Configure email or Slack webhook

### Alert 2: High Response Time
1. **Name**: High API Response Time
2. **Query**: Average response time > 1000ms
3. **Condition**: WHEN avg() OF query(A, 5m, now) IS ABOVE 1000
4. **Evaluate every**: 5m

### Alert 3: DAG Failure Rate
1. **Name**: DAG Failure Alert
2. **Query**: Failed DAG runs in last hour > 5
3. **Condition**: WHEN count() OF query(A, 1h, now) IS ABOVE 5

## Step 5: Configure Notifications

### Email Notifications
1. Go to **Alerting** → **Contact Points**
2. Click **New contact point**
3. **Name**: Email Alerts
4. **Type**: Email
5. Configure SMTP settings:
   - **SMTP Host**: smtp.gmail.com:587
   - **User**: your-email@gmail.com
   - **Password**: app-password
   - **From**: your-email@gmail.com
   - **To**: alerts@yourcompany.com

### Slack Notifications (optional)
1. **Type**: Slack
2. **Webhook URL**: Your Slack webhook URL
3. **Channel**: #alerts

## Step 6: Test Your Setup

### Test API Health Alert
1. Temporarily stop the financial API:
   ```bash
   docker-compose -f docker-compose.prod.yml stop financial-api
   ```
2. Wait 1-2 minutes for the alert to trigger
3. Check your email/Slack for the alert
4. Restart the API:
   ```bash
   docker-compose -f docker-compose.prod.yml start financial-api
   ```

### Test Dashboards
1. Generate some test predictions:
   ```bash
   curl -X POST http://localhost:8002/predict \
     -H "Content-Type: application/json" \
     -d '{"features": [100, 50, 25, 10, 5]}'
   ```
2. Refresh your Grafana dashboards to see the data

## Step 7: Production Checklist

- [ ] Grafana is accessible at http://localhost:3000
- [ ] PostgreSQL data source is connected
- [ ] Dashboards are created and showing data
- [ ] Alerts are configured and tested
- [ ] Notifications are working (email/Slack)
- [ ] Backup automation is scheduled (see separate guide)

## Next Steps

After completing this basic monitoring setup:
1. Add custom metrics from your FastAPI application
2. Set up log aggregation with Loki
3. Create more detailed dashboards for model performance
4. Add business metrics dashboards
5. Set up automated reporting

## Troubleshooting

### Common Issues
1. **Data source connection failed**: Check PostgreSQL container health
2. **No data in dashboards**: Ensure your application is logging metrics
3. **Alerts not firing**: Check alert conditions and evaluation intervals
4. **No notifications**: Verify contact point configuration

### Useful Commands
```bash
# Check Grafana logs
docker-compose -f docker-compose.prod.yml logs grafana

# Check PostgreSQL connection
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U airflow

# Restart Grafana
docker-compose -f docker-compose.prod.yml restart grafana
```

## Quick Start Summary

1. Open http://localhost:3000
2. Login with admin/admin
3. Add PostgreSQL data source
4. Create basic dashboards
5. Set up email alerts
6. Test with sample data

Your monitoring system will provide real-time insights into your automated cash flow pipeline's health and performance.