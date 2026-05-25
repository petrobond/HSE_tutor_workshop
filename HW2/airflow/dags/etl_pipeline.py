"""
Airflow DAG: ETL Pipeline — PostgreSQL → MinIO
Orchestrates: extract from PG → transform → load to MinIO as parquet
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# ============ Configuration ============
PG_CONN = "postgresql+psycopg2://analyst:analyst_pass@postgres:5432/oilfield"
MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS = "minioadmin"
MINIO_SECRET = "minioadmin"
BUCKET_NAME = "oilfield-data"

# Tables to extract
TABLES = [
    "wells", "production", "well_telemetry", "well_targets",
    "pumps", "pump_sensors", "pump_failures",
    "deliveries", "drivers", "vehicles", "oil_stations"
]

# Partitioning: table → date column
PARTITION_MAP = {
    "production": "date",
    "well_telemetry": "timestamp",
    "well_targets": "date",
    "deliveries": "date",
    "pump_sensors": "timestamp",
    "pump_failures": "failure_date",
}

# ============ Helper Functions ============

def get_s3_client():
    return boto3.client(
        "s3", endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET,
        region_name="us-east-1",
    )


def ensure_bucket():
    """Create bucket if not exists."""
    s3 = get_s3_client()
    buckets = [b['Name'] for b in s3.list_buckets().get('Buckets', [])]
    if BUCKET_NAME not in buckets:
        s3.create_bucket(Bucket=BUCKET_NAME)
        logger.info(f"Created bucket: {BUCKET_NAME}")
    else:
        logger.info(f"Bucket exists: {BUCKET_NAME}")


def save_parquet_to_minio(df, table_name, partition_col=None):
    """Save DataFrame to MinIO as parquet, optionally partitioned by date."""
    s3 = get_s3_client()

    if partition_col and partition_col in df.columns:
        date_series = pd.to_datetime(df[partition_col]).dt.date
        df = df.copy()
        df['_date'] = date_series

        for date_val, group in df.groupby('_date'):
            year = date_val.year
            month = f"{date_val.month:02d}"
            day = f"{date_val.day:02d}"
            key = f"{table_name}/year={year}/month={month}/day={day}/data.parquet"
            group_clean = group.drop(columns=['_date'])
            table = pa.Table.from_pandas(group_clean)
            buf = BytesIO()
            pq.write_table(table, buf, compression='snappy')
            buf.seek(0)
            s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=buf.read())

        logger.info(f"{table_name}: {len(df)} rows → {df['_date'].nunique()} partitions")
    else:
        key = f"{table_name}/data.parquet"
        table = pa.Table.from_pandas(df)
        buf = BytesIO()
        pq.write_table(table, buf, compression='snappy')
        buf.seek(0)
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=buf.read())
        logger.info(f"{table_name}: {len(df)} rows (no partitioning)")


# ============ Task Functions ============

def extract_all_tables(**context):
    """Extract all tables from PostgreSQL into XCom as dict of DataFrames (JSON-serializable problems → use file-based transfer)."""
    engine = create_engine(PG_CONN)
    execution_date = context['ds']  # YYYY-MM-DD
    context['task_instance'].xcom_push(key='execution_date', value=execution_date)

    for table_name in TABLES:
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        logger.info(f"Extracted {table_name}: {df.shape}")
        # Save to a temp path for inter-task sharing (parquet in /tmp)
        path = f"/tmp/{table_name}.parquet"
        df.to_parquet(path, index=False)
        context['task_instance'].xcom_push(key=f"extracted_{table_name}_rows", value=len(df))

    logger.info(f"Extraction complete. {len(TABLES)} tables processed.")


def transform_data(**context):
    """Minimal transformation: handle NULLs, cast types."""
    for table_name in TABLES:
        path = f"/tmp/{table_name}.parquet"
        df = pd.read_parquet(path)

        # Basic cleaning
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'failure_date' in df.columns:
            df['failure_date'] = pd.to_datetime(df['failure_date'])

        df.to_parquet(path, index=False)
        logger.info(f"Transformed {table_name}: {df.shape}")

    context['task_instance'].xcom_push(key='transform_status', value='success')


def load_to_minio(**context):
    """Load all transformed DataFrames to MinIO."""
    ensure_bucket()

    for table_name in TABLES:
        path = f"/tmp/{table_name}.parquet"
        df = pd.read_parquet(path)
        partition_col = PARTITION_MAP.get(table_name, None)
        save_parquet_to_minio(df, table_name, partition_col=partition_col)

    context['task_instance'].xcom_push(key='load_status', value='success')
    logger.info("Load to MinIO complete.")


def verify_load(**context):
    """Verify that files exist in MinIO."""
    s3 = get_s3_client()
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET_NAME)
    object_count = 0
    for page in pages:
        object_count += len(page.get('Contents', []))

    logger.info(f"Verification: {object_count} objects in bucket {BUCKET_NAME}")
    if object_count == 0:
        raise ValueError("No objects found in MinIO — load may have failed!")
    context['task_instance'].xcom_push(key='minio_object_count', value=object_count)


# ============ DAG Definition ============

default_args = {
    'owner': 'hse_student',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

with DAG(
    dag_id='etl_pg_to_minio',
    default_args=default_args,
    description='ETL: PostgreSQL → Pandas → MinIO (Parquet)',
    schedule_interval='@daily',  # Daily incremental
    max_active_runs=1,
    tags=['hw2', 'etl'],
) as dag:

    task_extract = PythonOperator(
        task_id='extract_pg',
        python_callable=extract_all_tables,
        provide_context=True,
    )

    task_transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    task_load = PythonOperator(
        task_id='load_to_minio',
        python_callable=load_to_minio,
        provide_context=True,
    )

    task_verify = PythonOperator(
        task_id='verify_load',
        python_callable=verify_load,
        provide_context=True,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    task_extract >> task_transform >> task_load >> task_verify