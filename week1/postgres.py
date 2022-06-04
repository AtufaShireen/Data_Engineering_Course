
import pandas as pd
from sqlalchemy import create_engine


df = pd.read_csv('/Users/atufashireen/projects/DE_ZoomCamp/datasets/taxi-zone-lookup.csv')

# df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
# df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
# print(pd.io.sql.get_schema(df,name='yello_dataset'))


# from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

df.to_sql(name='zones', con=engine, if_exists='replace')

