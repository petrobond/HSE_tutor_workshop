"""
Airflow DAG: Data Quality Checks
Checks NULL %, outlier detection, and expected value ranges.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

PG_CONN = "postgresql+psycopg2://analyst:analyst_pass@postgres:5432/oilfield"

# Quality thresholds
NULL_PCT_THRESHOLD = 10.0  # Max % NULLs allowed per column
OUTLIER_IQR_THRESHOLD = 3.0  # IQR multiplier for outlier detection

# Tables to check
TABLES_TO_CHECK = {
    "production": ["well_id", "date", "oil_ton", "gas_m3", "water_m3", "energy_kwh", "downtime_hours", "temperature", "pressure"],
    "well_telemetry": ["well_id", "timestamp", "pump_speed_rpm", "pump_current", "pressure_in", "pressure_out", "temperature", "vibration", "oil_flow_rate"],
    "pump_sensors": ["pump_id", "timestamp", "temperature", "vibration", "current", "rpm", "pressure"],
    "deliveries": ["date", "source", "destination", "product_type", "volume_ton", "cost_usd", "delay_hours", "distance_km", "weather_conditions"],
}

EXPECTED_RANGES = {
    "oil_ton": (0, 500),
    "gas_m3": (0, 100000),
    "temperature": (0, 200),
    "pressure": (0, 200),
    "vibration": (0, 50),
    "rpm": (0, 3000),
    "current": (0, 100),
    "volume_ton": (0, 50),
    "cost_usd": (0, 5000),
    "delay_hours": (0, 24),
    "distance_km": (0, 500),
}


def check_null_percentages(**context):
    """Check NULL % for each column in monitored tables."""
    engine = create_engine(PG_CONN)
    results = []

    for table, columns in TABLES_TO_CHECK.items():
        df = pd.read_sql(f"SELECT * FROM {table}", engine)
        for col in columns:
            null_pct = df[col].isnull().mean() * 100
            status = "PASS" if null_pct <= NULL_PCT_THRESHOLD else "FAIL"
            if null_pct > NULL_PCT_THRESHOLD:
                logger.warning(f"DQ FAIL: {table}.{col} has {null_pct:.1f}% NULLs (threshold {NULL_PCT_THRESHOLD}%)")
            results.append({"table": table, "column": col, "null_pct": round(null_pct, 2), "status": status})

    df_results = pd.DataFrame(results)
    fails = df_results[df_results['status'] == 'FAIL']
    logger.info(f"NULL check: {len(df_results)} columns checked, {len(fails)} failures")
    if len(fails) > 0:
        logger.warning(f"Failures:\n{fails.to_string()}")
    context['task_instance'].xcom_push(key='null_check_failures', value=len(fails))


def check_outliers(**context):
    """Detect outliers via IQR method."""
    engine = create_engine(PG_CONN)
    outlier_results = []

    for table, columns in TABLES_TO_CHECK.items():
        df = pd.read_sql(f"SELECT * FROM {table}", engine)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.intersection(columns)
        for col in numeric_cols:
            if df[col].isnull().all():
                continue
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue
            lower = Q1 - OUTLIER_IQR_THRESHOLD * IQR
            upper = Q3 + OUTLIER_IQR_THRESHOLD * IQR
            outlier_count = ((df[col] < lower) | (df[col] > upper)).sum()
            outlier_pct = outlier_count / len(df) * 100
            outlier_results.append({
                "table": table, "column": col,
                "outlier_count": outlier_count, "outlier_pct": round(outlier_pct, 2),
                "lower_bound": round(lower, 2), "upper_bound": round(upper, 2)
            })

    df_out = pd.DataFrame(outlier_results)
    high_outliers = df_out[df_out['outlier_pct'] > 5]
    logger.info(f"Outlier check: {len(df_out)} columns checked")
    if len(high_outliers) > 0:
        logger.warning(f"High-outlier columns (>5%):\n{high_outliers.to_string()}")
    context['task_instance'].xcom_push(key='outlier_warnings', value=len(high_outliers))


def check_value_ranges(**context):
    """Verify values are within expected ranges."""
    engine = create_engine(PG_CONN)
    range_results = []

    for table, columns in TABLES_TO_CHECK.items():
        df = pd.read_sql(f"SELECT * FROM {table}", engine)
        for col, (low, high) in EXPECTED_RANGES.items():
            if col not in df.columns:
                continue
            valid_data = df[col].dropna()
            if len(valid_data) == 0:
                continue
            below_min = (valid_data < low).sum()
            above_max = (valid_data > high).sum()
            in_range_pct = (len(valid_data) - below_min - above_max) / len(valid_data) * 100
            status = "PASS" if in_range_pct >= 95 else "FAIL"
            range_results.append({
                "table": table, "column": col,
                "expected_range": f"[{low}, {high}]",
                "in_range_pct": round(in_range_pct, 2),
                "below_min": below_min, "above_max": above_max,
                "status": status,
            })

    df_range = pd.DataFrame(range_results)
    fails = df_range[df_range['status'] == 'FAIL']
    logger.info(f"Range check: {len(df_range)} columns checked, {len(fails)} failures")
    if len(fails) > 0:
        logger.warning(f"Range failures:\n{fails.to_string()}")
    context['task_instance'].xcom_push(key='range_check_failures', value=len(fails))


def quality_summary(**context):
    """Generate final QA report."""
    ti = context['task_instance']
    null_fails = ti.xcom_pull(key='null_check_failures', task_ids='check_null_pct')
    outlier_warns = ti.xcom_pull(key='outlier_warnings', task_ids='check_outliers')
    range_fails = ti.xcom_pull(key='range_check_failures', task_ids='check_value_ranges')

    total_issues = (null_fails or 0) + (outlier_warns or 0) + (range_fails or 0)
    logger.info(f"=== DQ SUMMARY === Total issues: {total_issues}")

    if total_issues > 0:
        logger.warning("Data quality issues found. Check logs for details.")

    context['task_instance'].xcom_push(key='dq_total_issues', value=total_issues)


# ============ DAG ============
default_args = {
    'owner': 'hse_student',
    'start_date': datetime(2025, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='data_quality_checks',
    default_args=default_args,
    description='Data Quality: NULL %, outliers, range checks',
    schedule_interval='@daily',
    catchup=False,
    tags=['hw2', 'dq'],
) as dag:

    t1 = PythonOperator(task_id='check_null_pct', python_callable=check_null_percentages, provide_context=True)
    t2 = PythonOperator(task_id='check_outliers', python_callable=check_outliers, provide_context=True)
    t3 = PythonOperator(task_id='check_value_ranges', python_callable=check_value_ranges, provide_context=True)
    t4 = PythonOperator(task_id='quality_summary', python_callable=quality_summary, provide_context=True,
                        trigger_rule=TriggerRule.ALL_DONE)

    t1 >> t2 >> t3 >> t4