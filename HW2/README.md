# HW2: Big Data & ML — Oilfield Data Pipeline

**HSE Tutor Workshop • Data Engineering & ML**

Full analytical pipeline: PostgreSQL → ETL → MinIO → Jupyter → Superset + Airflow

---

## Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐
│ Postgres │────▶│  ETL     │────▶│  MinIO   │────▶│  Jupyter     │
│ (source) │     │ (pandas) │     │ (parquet)│     │  (analysis)  │
└──────────┘     └──────────┘     └──────────┘     └──────┬───────┘
       ▲                                                   │
       │              ┌──────────┐                         ▼
       └──────────────│ Airflow  │◀─────────────── ┌──────────────┐
                      │ (DAGs)   │                  │  Superset    │
                      └──────────┘                  │  (dashboards)│
                                                    └──────────────┘
```

## Quick Start

### Prerequisites
- Docker Desktop 4.x+ with 8+ GB RAM allocated
- Git

### Start the infrastructure

```bash
cd HW2
docker compose up -d
```

Wait 1-2 minutes for all services to initialize.

### Services & Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **JupyterHub** | http://localhost:8000 | Token: `hse_token` |
| **MinIO Console** | http://localhost:9001 | `minioadmin` / `minioadmin` |
| **Superset** | http://localhost:8088 | `admin` / `admin` |
| **Airflow** | http://localhost:8080 | `admin` / `admin` |
| **PostgreSQL** | localhost:5432 | `analyst` / `analyst_pass` / `oilfield` |

### Stop everything

```bash
docker compose down -v  # -v removes volumes (clean state)
```

---

## Project Structure

```
HW2/
├── docker-compose.yml              # All services (PG, MinIO, Jupyter, Superset, Airflow)
├── .gitignore
├── README.md
│
├── docker/
│   └── postgres/init/
│       ├── 01_tables.sql           # DDL: all 12 tables
│       └── 02_data.sql             # INSERT: synthetic oilfield data
│
├── notebooks/                      # Jupyter notebooks (run in order)
│   ├── 00_setup_connections.ipynb         # Verify PG & MinIO connections
│   ├── 01_etl_to_minio.ipynb              # ETL: PG → Parquet in MinIO (partitioned)
│   ├── 02_task1_production_analytics.ipynb # Task 1: Production KPIs & dashboards
│   ├── 03_task2_debit_prediction.ipynb     # Task 2: ML flow rate prediction
│   ├── 04_task3_anomaly_detection.ipynb    # Task 3: Pump anomaly & failure prediction
│   └── 05_task4_logistics.ipynb            # Task 4: Logistics & delivery analytics
│
├── airflow/dags/                   # Airflow DAGs (Advanced — 10 points)
│   ├── etl_pipeline.py             # Main ETL orchestration
│   ├── data_quality_checks.py      # NULL %, outliers, range validation
│   └── incremental_load.py         # Watermark-based incremental loading
│
└── superset/dashboards/            # Superset dashboard exports (JSON)
```

---

## Tasks Overview

### Task 1 — Production Analytics
- **Data:** `wells` + `production` (5 wells × 30 days)
- **Analysis:** Daily totals, KPI per well, best/worst wells, temperature × pressure impact
- **Cleaning:** NULL handling (Well-304 suspended), IQR outlier detection
- **Data mart:** `mart_production` (daily_total.parquet + well_kpi.parquet)
- **Superset charts:** Line chart (daily production), Bar chart (top wells), Heatmap (pressure vs flow rate)

### Task 2 — ML Flow Rate Prediction
- **Data:** `well_telemetry` (hourly) → aggregated to daily features + `well_targets`
- **Models:** Linear Regression, Random Forest Regressor (scikit-learn)
- **Metrics:** MAE, RMSE, R²
- **Features:** avg pressure, temperature, pump speed, vibration, pump current
- **Superset charts:** Actual vs Predicted scatter, error over time

### Task 3 — Anomaly Detection & Pump Failures
- **Data:** `pump_sensors` (3 pumps, 3-minute interval) + `pump_failures` (3 known failures)
- **Methods:** Z-score (≥2 metrics flagged), Isolation Forest (contamination 5%)
- **Pre-failure analysis:** Vibration/temperature ramp-up in hours before failure
- **Model:** Random Forest Classifier → failure probability per pump
- **Data mart:** `mart_failures` (anomalies_zscore.parquet + pump_risk_scores.parquet)
- **Superset charts:** Anomalies timeline, vibration ramp-up, risk scores

### Task 4 — Logistics & Deliveries
- **Data:** `deliveries` (30 trips) + `drivers` (5) + `vehicles` (5) + `oil_stations` (20)
- **Analysis:** Delay factors (weather, distance, driver experience), cost/km, route efficiency
- **Data mart:** `mart_logistics` (kpi_driver, weather_delay, route_summary, daily_volume)
- **Superset charts:** Delay vs Weather, Cost vs Distance, Driver KPI

---

## Advanced Features (for 10 points)

1. **Airflow DAGs:**
   - `etl_pipeline.py` — full orchestration: extract → transform → load → verify
   - `data_quality_checks.py` — NULL %, IQR outlier detection, expected range validation
   - `incremental_load.py` — watermark-based loading of only new/changed data

2. **Data Quality:**
   - NULL percentage checks (threshold 10%)
   - Outlier detection via IQR
   - Value range validation against expected bounds

3. **Data Marts in MinIO:**
   - `marts/mart_production/` — daily_total.parquet, well_kpi.parquet
   - `marts/mart_failures/` — anomalies_zscore.parquet, pump_risk_scores.parquet
   - `marts/mart_logistics/` — kpi_driver.parquet, weather_delay.parquet, route_summary.parquet

4. **Hive-style partitioning:**
   - Fact tables partitioned as `table/year=YYYY/month=MM/day=DD/data.parquet`

---

## Technologies Used

| Category | Tools |
|----------|-------|
| Infrastructure | Docker Compose, PostgreSQL 15, MinIO (S3-compatible) |
| ETL | pandas, pyarrow, boto3 |
| ML | scikit-learn (LinearRegression, RandomForest, IsolationForest) |
| Visualization | matplotlib, seaborn, plotly |
| Orchestration | Apache Airflow 2.9 |
| BI | Apache Superset |
| Format | Parquet (Snappy compression) |

---

## Superset Dashboard Setup

After running notebooks, configure Superset:

1. **Add PostgreSQL connection** in Superset:
   - Database: `postgresql+psycopg2://analyst:analyst_pass@postgres:5432/oilfield`

2. **Create datasets** from PostgreSQL tables or import parquet files via MinIO

3. **Build dashboards** for each task:
   - **Production Dashboard:** Line chart (daily oil), Bar chart (top wells), Heatmap
   - **ML Dashboard:** Actual vs Predicted scatter, Error timeline
   - **Anomaly Dashboard:** Anomaly timeline, Vibration ramp-up, Risk scores
   - **Logistics Dashboard:** Delay vs Weather, Cost vs Distance, Driver KPIs

---

## Submission Checklist

- [x] `docker-compose.yml`
- [x] ETL scripts (notebook `01_etl_to_minio.ipynb`)
- [x] Jupyter notebooks (Tasks 1-4)
- [x] ML models + metrics (Task 2 & 3)
- [x] Superset dashboards (described above)
- [x] Airflow DAGs (ETL, DQ, Incremental)
- [x] Data marts (mart_production, mart_failures, mart_logistics)
- [x] Data Quality checks
- [x] Incremental load
- [x] README.md
- [x] .gitignore