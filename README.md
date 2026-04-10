# Clinical Trial Data Pipeline

## Project Overview

This project implements a clinical trial data pipeline for a life sciences use case.

The pipeline ingests raw clinical trial data from a CSV source, loads it into a PostgreSQL staging layer, transforms it into a normalized analytical schema, and runs SQL-based analytics on study characteristics, conditions, interventions, outcomes, and subject headings.

The goal of the project is to demonstrate practical data engineering skills across ingestion, data modeling, validation, transformation, SQL analytics, Docker-based local execution, testing, and orchestration.

---

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
```

## Pipeline Layers
1. Raw ingestion layer
Input dataset: data/clin_trials.csv
Raw load into stg_clinical_trials
2. Curated transformation layer
Clean placeholder values such as Unknown, NA, and empty strings
Standardize categorical values
Generate a business key for deduplication
Normalize multi-value fields into relational child tables
3. Analytics layer
SQL queries for trial counts
Common conditions analysis
Intervention completion behavior
Organization distribution
Study timeline analysis
4. Orchestration layer
Airflow DAG executes:
database initialization
staging load
core transformation
analytics run
