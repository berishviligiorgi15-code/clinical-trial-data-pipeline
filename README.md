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
staging load
core transformation
analytics run
