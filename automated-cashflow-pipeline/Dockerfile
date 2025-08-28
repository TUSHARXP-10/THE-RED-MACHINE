FROM apache/airflow:2.8.1-python3.10

USER airflow

RUN pip install --no-cache-dir \
    scikit-learn \
    statsmodels \
    pmdarima \
    xgboost \
    tensorflow \
    textblob \
    riskfolio-lib \
    mlflow

USER root

RUN apt-get update && apt-get install -y git