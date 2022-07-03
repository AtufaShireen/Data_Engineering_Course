from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from ingest_script import ingest_callable
import os


PG_HOST=os.environ.get('PG_HOST')
PG_USER=os.environ.get('PG_USER')
PG_PASSWORD=os.environ.get('PG_PASSWORD')
PG_PORT=os.environ.get('PG_PORT')
PG_DATABASE=os.environ.get('PG_DATABASE')


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME","/opt/airflow/")
url_prefix = 'https://nyc-tlc.s3.amazonaws.com/trip+data'
url = url_prefix+ "/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet"
output_template = AIRFLOW_HOME+'/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
table_template = 'yellow_taxi_{{  execution_date.strftime(\'%Y-%m\') }}'
default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

local_workflow = DAG(
    dag_id = "local_ingest",
    schedule_interval = "0 0 2 * *",
    default_args = default_args,
    catchup = False,
    max_active_runs  = 1,
    tags = ['dag-1']
)

with local_workflow:
    wget_task = BashOperator(
        task_id='wget',
        bash_command='echo hello'
        #f'curl -sSL {url} > {output_template}'
    )
    ingest_task = PythonOperator(
        task_id = "format_parquet",
        python_callable = ingest_callable,
        op_kwargs = dict(
         user=PG_USER,
         password=PG_PASSWORD,
         host=PG_HOST,
         port=PG_PORT,
         db = PG_DATABASE,
         table_name=table_template,
        par_file=output_template)
    )
    wget_task >> ingest_task