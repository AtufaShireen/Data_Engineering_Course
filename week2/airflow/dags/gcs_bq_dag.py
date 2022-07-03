import logging
import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
path_local_home = os.environ.get("AIRFLOW_HOME","/opt/airflow/")


dataset_file  = "yellow_tripdata_2021-01.parquet"
dataset_url = f"https://s3.amazonaws.com/nyc-tlc/trip+data/{dataset_file}"#"/trip_data/yellow_tripdata_2021-01.parquet"#f"https://s3.amazonaws.com/nyc-tlc/trip+data/{dataset_file}"
parquet_file = dataset_file


path_credits = f"{path_local_home}/google_credentials.json"
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET","trips_data_all")

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}
