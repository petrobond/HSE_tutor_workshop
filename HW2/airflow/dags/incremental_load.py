"""
Airflow DAG: Incremental Load Pipeline
Loads only new/changed data using watermark (max date/timestamp) tracking.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

import pandas as pd
from sqlalchemy import create_engine, text
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

PG_CONN = "postgresql+psycopg2://analyst:analyst_pass@postgres:5432/oilfield"
MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS = "minioadmin"
MINIO_SECRET = "minioadmin"
BUCKET_NAME = "oilfield-data"

# Tables supporting incremental load (have date/timestamp column)
INCREMENTAL_TABLES = {
    "production": "date",
    "well_telemetry": "timestamp",
    "well_targets": "date",
    "deliveries": "date",
    "pump_sensors": "timestamp",
    "pump_failures": "failure_date",
}


def get_watermark(table_name):
    """Get last loaded date/timestamp from Airflow Variables."""
    try:
        return Variable.get(f"watermark_{table_name}", default_var=None)
    except Exception:
        return None


def set_watermark(table_name, value):
    """Update watermark for the table."""
    Variable.set(f"watermark_{table_name}", str(value))


def incremental_extract_and_load(**context):
    """Extract only new records since last watermark, load to MinIO."""
    engine = create_engine(PG_CONN)
    s3 = boto3.client("s3", endpoint_url=MINIO_ENDPOINT,
                      aws_access_key_id=MINIO_ACCESS,
                      aws_secret_access_key=MINIO_SECRET,
                      region_name="us-east-1")

    # Ensure bucket exists
    buckets = [b['Name'] for b in s3.list_buckets().get('Buckets', [])]
    if BUCKET_NAME not in buckets:
        s3.create_bucket(Bucket=BUCKET_NAME)

    total_new_rows = 0

    for table_name, date_col in INCREMENTAL_TABLES.items():
        watermark = get_watermark(table_name)
        logger.info(f"Table: {table_name}, watermark: {watermark}")

        if watermark:
            query = f"SELECT * FROM {table_name} WHERE {date_col} > :watermark"
            df = pd.read_sql(text(query), engine, params={"watermark": watermark})
        else:
            # First run — load everything
            df = pd.read_sql(f"SELECT * FROM {table_name}", engine)

        if len(df) == 0:
            logger.info(f"  {table_name}: no new records")
            continue

        # Convert date column
        df[date_col] = pd.to_datetime(df[date_col])

        # Save to MinIO with partitioning by date
        date_series = df[date_col].dt.date
        df = df.copy()
        df['_date'] = date_series

        for date_val, group in df.groupby('_date'):
            year = date_val.year
            month = f"{date_val.month:02d}"
            day = f"{date_val.day:02d}"
            key = f"{table_name}/year={year}/month={month}/day={day}/data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            group_clean = group.drop(columns=['_date'])
            table = pa.Table.from_pandas(group_clean)
            buf = BytesIO()
            pq.write_table(table, buf, compression='snappy')
            buf.seek(0)
            s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=buf.read())

        # Update watermark
        new_watermark = str(df[date_col].max())
        set_watermark(table_name, new_watermark)

        logger.info(f"  {table_name}: loaded {len(df)} new rows, new watermark: {new_watermark}")
        total_new_rows += len(df)

    logger.info(f"Incremental load complete. Total new rows: {total_new_rows}")
    context['task_instance'].xcom_push(key='incremental_rows', value=total_new_rows)


# ============ DAG ============
default_args = {
    'owner': 'hse_student',
    'start_date': datetime(2025, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='incremental_load',
    default_args=default_args,
    description='Incremental load: only new data since last watermark',
    schedule_interval='@hourly',
    catchup=False,
    tags=['hw2', 'incremental'],
) as dag:

    task_incremental = PythonOperator(
        task_id='incremental_extract_load',
        python_callable=incremental_extract_and_load,
        provide_context=True,
    )