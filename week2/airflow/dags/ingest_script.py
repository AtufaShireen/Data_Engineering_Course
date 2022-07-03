import argparse
import os
import pyarrow.parquet as pq
import pandas as pd
from sqlalchemy import create_engine



def ingest_callable(user, password, host, port, db, table_name,par_file):
    print(f"Table: {table_name}, Host:{host}, FILEname: {par_file} ")
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    # parquet_table = pq.read_table(filename)
    # df = parquet_table.to_pandas()

    # df.head(n=5000).to_sql(name="yellow_taxi_data", con=engine, if_exists='append', chunksize=100000)

 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the parquet file')

    args = parser.parse_args()

    ingest_callable(args)