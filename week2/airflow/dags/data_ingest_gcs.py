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


#store only first 1000 records
def format_to_parquet(src_file):
    if not src_file.endswith(".parquet"):
        logging.error("can only accept parquet files!")
        return
    table = pq.read_table(src_file)
    table = table[0:1000]
    pq.write_table(table,src_file)



# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    print("Important: ", local_file)
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


with DAG(
    dag_id = "data_ingest_gcs",
    schedule_interval = "@daily",
    default_args = default_args,
    catchup = False,
    max_active_runs  = 1,
    tags = ['dag-1']
) as dag:
    download_dataset = BashOperator(
            task_id = "download_dataset_task",
            bash_command = f"curl -sSL {dataset_url} > {path_local_home}/{dataset_file}" #f"cp {dataset_url} {path_local_home}/{dataset_file}"
            
    )
    format_to_parquet = PythonOperator(
        task_id = "format_parquet_task",
        python_callable = format_to_parquet,
        op_kwargs = {
            "src_file":f"{path_local_home}/{dataset_file}"
        }
    )
    local_gcs = PythonOperator(
        task_id = "local_to_gcs_task",
        python_callable = upload_to_gcs,
        op_kwargs = {
            'bucket':BUCKET,
            'object_name':f"raw/{parquet_file}",
            'local_file': f"{path_local_home}/{parquet_file}"
        }
    )
    bigquery_external_table = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
            },
        },
    )
    download_dataset >> format_to_parquet >> local_gcs >>bigquery_external_table
