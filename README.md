## Project Overview

This project implements a clinical trial data pipeline for a life sciences use case.

The pipeline ingests raw clinical trial data from a CSV source,
loads it into a PostgreSQL staging layer,
transforms it into a normalized analytical schema,
and runs SQL-based analytics on study characteristics,
conditions, interventions, outcomes, and subject headings.

The goal of the project is to demonstrate practical
data engineering skills across ingestion, data modeling, validation,
transformation, SQL analytics, Docker-based local execution, testing, and
orchestration.

## Dataset

The original `clin_trials.csv` file is not included in this repository because it exceeds GitHub’s file size limits.

Place the dataset manually in:

`data/clin_trials.csv`

You can also use a smaller sample file for testing.

## Architecture

High-level flow:

`CSV source -> staging table -> normalized core tables -> analytics queries -> Airflow orchestration`

```mermaid
flowchart LR
    A[CSV Source: clin_trials.csv] --> B[Staging Table: stg_clinical_trials]
    B --> C[Transform and Clean]
    C --> D[studies]
    C --> E[conditions + study_conditions]
    C --> F[interventions + study_interventions]
    C --> G[outcomes]
    C --> H[mesh_terms + study_mesh_terms]
    D --> I[Analytics Queries]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J[Airflow DAG Orchestration]
Pipeline layers
Raw ingestion layer
Input dataset: data/clin_trials.csv
Raw load into stg_clinical_trials
Curated transformation layer
Clean placeholder values such as Unknown, NA, and empty strings
Standardize categorical values
Generate a business key for deduplication
Normalize multi-value fields into relational child tables
Analytics layer
SQL queries for trial counts, common conditions, intervention completion behavior, organization distribution, and study timeline analysis
Orchestration layer
Airflow DAG executes:
database initialization
staging load
core transformation
analytics run
Project Structure
clinical-trial-pipeline/
├── dags/
│   └── clinical_trials_pipeline.py
├── data/
│   └── clin_trials.csv
├── src/
│   ├── analytics/
│   │   ├── analytics.sql
│   │   └── run_analytics.py
│   ├── db/
│   │   ├── connection.py
│   │   ├── init_db.py
│   │   └── schema.sql
│   ├── ingestion/
│   │   └── load_csv_to_staging.py
│   ├── transform/
│   │   └── transform_trials.py
│   └── utils/
│       └── helpers.py
├── tests/
│   └── test_helpers.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
Data Model
The source file is a denormalized study-level CSV, so the target model separates raw ingestion from curated analytical tables.
Staging
stg_clinical_trials
Core tables
studies
conditions
study_conditions
interventions
study_interventions
outcomes
mesh_terms
study_mesh_terms
Design decisions
A staging table is used to preserve raw source values and simplify reprocessing/debugging.
A surrogate primary key (study_id) is used in the curated model.
Because the dataset does not provide a reliable natural study identifier in the provided CSV, a business key is generated from:
brief_title
organization_full_name
start_date_raw
Multi-valued source columns such as conditions, interventions, and medical subject headings are normalized into dimension and bridge tables.
Outcome measures are stored as child rows because they are high-cardinality free text.
Data Cleaning and Transformation Rules
The pipeline applies the following transformation rules:
Convert placeholder values such as Unknown, NA, N/A, null, and empty strings to NULL
Normalize categorical values to uppercase underscore format where appropriate
Parse start_date_raw into:
start_date
start_date_precision
Split multi-valued columns using comma-based parsing for the MVP
Deduplicate studies using the generated business key
Preserve long free-text intervention descriptions in the studies table
Analytics Implemented
The project includes SQL queries for:
Trials by study type and phase
Most common conditions being studied
Interventions with highest completion counts and completion rates
Organization distribution by organization class
Timeline analysis by study start year
Sample Results Summary
On the processed dataset, the pipeline produced approximately:
495,558 studies
110,162 distinct conditions
443,231 distinct interventions
479,135 outcomes
63,520 medical subject heading terms
Initial analytics showed that:
INTERVENTIONAL and OBSERVATIONAL are the dominant study types
common conditions include Healthy, Breast Cancer, Obesity, and Diabetes Mellitus
organization classes are dominated by OTHER, followed by INDUSTRY and NIH
Local Setup Instructions
Prerequisites
Python 3.13
Docker Desktop
1. Start services
docker compose up -d --build
2. Create Airflow admin user and initialize metadata
docker compose up airflow-init
3. Open Airflow UI
Open:
http://localhost:8080
4. Login to Airflow
Use:
Username: admin
Password: admin
5. Trigger the DAG
Run the clinical_trials_pipeline DAG from the Airflow UI.
Manual Script Execution
The pipeline can also be executed directly without Airflow.
1. Create database schema
python3 -m src.db.init_db
2. Load raw CSV into staging
python3 -m src.ingestion.load_csv_to_staging
3. Transform staged data into core tables
python3 -m src.transform.transform_trials
4. Run analytics
python3 -m src.analytics.run_analytics
Docker
This project uses Docker for:
PostgreSQL
Airflow webserver
Airflow scheduler
Airflow initialization
Start all services
docker compose up -d --build
Check running containers
docker ps
Airflow Orchestration
The Airflow DAG is located at:
dags/clinical_trials_pipeline.py
Task order
init_db
load_staging
transform_core
run_analytics
This allows the full pipeline to be executed as a single orchestrated workflow.
Testing
Unit tests are included for core helper functions such as:
placeholder normalization
category normalization
date parsing
multi-value splitting
business key generation
Run tests with:
pytest tests/test_helpers.py
Current Status
Implemented
CSV ingestion into PostgreSQL staging
normalized core schema
data cleaning and transformation
SQL analytics queries
Dockerized PostgreSQL local setup
Dockerized Airflow orchestration
Airflow DAG execution
unit tests for helper functions
Deferred to future iteration
API ingestion
SQL source ingestion
production-grade logging and monitoring
stronger integration and data-quality testing
Trade-offs and Limitations
This solution is intentionally scoped as an MVP.
Trade-offs made
The primary implemented source is CSV, even though the challenge also mentions JSON APIs and SQL databases.
Multi-value parsing uses comma-based splitting, which is simple but not semantically perfect for all medical text.
Geographic analysis was not implemented because the chosen dataset does not expose clear location fields in the provided CSV structure.
The generated business key is a practical surrogate for deduplication, but not a perfect replacement for a true source identifier such as an NCT ID.
Airflow uses SQLite metadata and SequentialExecutor in the local demo environment for simplicity, even though production would require a stronger setup.
Limitations
No production-grade logging framework yet
No incremental loading strategy yet
No data quality audit table yet
No API ingestion module implemented in the final MVP
No SQL source ingestion module implemented in the final MVP
No production-grade Airflow metadata backend yet
Time Allocation Breakdown
Approximate time allocation:
Setup and architecture: 20%
Schema design and transformation logic: 35%
Data loading and debugging: 20%
Analytics and validation: 10%
Airflow and Docker orchestration: 10%
Testing and documentation: 5%
Scalability: How would this handle 100x more data?
For 100x data volume, I would:
move from full reload to incremental or CDC-style ingestion
partition large tables by date or domain-specific keys
use bulk loading (COPY) and batch-oriented transformations
push more transformations into SQL and database-native set-based operations
add orchestration retries, SLAs, and alerting
introduce indexing review and query-plan optimization
consider a warehouse/lakehouse architecture for analytical workloads
Data Quality: Additional validation rules for clinical trial data
I would add:
stricter status-domain validation
valid phase-value enforcement
title length and non-empty content checks
date consistency checks
duplicate-study anomaly detection
stronger parsing/validation for multi-valued fields
source-level audit tables for rejected/flagged rows
Compliance: GxP considerations
In a GxP-regulated environment, I would add:
full audit trails for ingestion and transformation
versioned datasets and reproducible pipeline runs
controlled deployment and change management
validated scripts and environments
access control and separation of duties
documented test evidence and approval workflow
Monitoring: Production monitoring approach
In production, I would monitor:
pipeline run status and duration
source row counts vs loaded row counts
rejected/null/invalid record rates
duplicate rates
freshness / latency metrics
SQL query performance
infrastructure health
alerting for failures and abnormal data-quality drift
Security: Sensitive clinical data protections
For sensitive clinical data, I would implement:
least-privilege DB access
secrets management instead of plaintext env files
encryption at rest and in transit
network restrictions
audit logging
PII/PHI classification and masking where needed
role-based access to raw vs curated layers
Execution Notes
This project was implemented as modular Python scripts first and then orchestrated with Dockerized Airflow. This approach kept development and debugging straightforward while still demonstrating orchestration design and end-to-end automated execution.