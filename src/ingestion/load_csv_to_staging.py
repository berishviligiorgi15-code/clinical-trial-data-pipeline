import os
import pandas as pd
from dotenv import load_dotenv

from src.db.connection import get_connection


load_dotenv()


COLUMN_MAPPING = {
    "Organization Full Name": "organization_full_name",
    "Organization Class": "organization_class",
    "Responsible Party": "responsible_party",
    "Brief Title": "brief_title",
    "Full Title": "full_title",
    "Overall Status": "overall_status",
    "Start Date": "start_date_raw",
    "Standard Age": "standard_age_raw",
    "Conditions": "conditions_raw",
    "Primary Purpose": "primary_purpose",
    "Interventions": "interventions_raw",
    "Intervention Description": "intervention_description_raw",
    "Study Type": "study_type",
    "Phases": "phases_raw",
    "Outcome Measure": "outcome_measure_raw",
    "Medical Subject Headings": "medical_subject_headings_raw",
}


def load_csv() -> pd.DataFrame:
    csv_file_path = os.getenv("CSV_FILE_PATH")

    df = pd.read_csv(csv_file_path)
    df = df.rename(columns=COLUMN_MAPPING)

    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "row_num"})
    elif "row_num" not in df.columns:
        df.insert(0, "row_num", range(len(df)))

    df["source_file_name"] = os.path.basename(csv_file_path)

    expected_columns = [
        "row_num",
        "organization_full_name",
        "organization_class",
        "responsible_party",
        "brief_title",
        "full_title",
        "overall_status",
        "start_date_raw",
        "standard_age_raw",
        "conditions_raw",
        "primary_purpose",
        "interventions_raw",
        "intervention_description_raw",
        "study_type",
        "phases_raw",
        "outcome_measure_raw",
        "medical_subject_headings_raw",
        "source_file_name",
    ]

    return df[expected_columns]


def insert_staging_data(df: pd.DataFrame) -> None:
    insert_sql = """
        INSERT INTO stg_clinical_trials (
            row_num,
            organization_full_name,
            organization_class,
            responsible_party,
            brief_title,
            full_title,
            overall_status,
            start_date_raw,
            standard_age_raw,
            conditions_raw,
            primary_purpose,
            interventions_raw,
            intervention_description_raw,
            study_type,
            phases_raw,
            outcome_measure_raw,
            medical_subject_headings_raw,
            source_file_name
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    records = df.where(pd.notnull(df), None).values.tolist()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("TRUNCATE TABLE stg_clinical_trials;")
        cur.executemany(insert_sql, records)
        conn.commit()
        print(f"Loaded {len(records)} rows into stg_clinical_trials.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def main():
    df = load_csv()
    insert_staging_data(df)


if __name__ == "__main__":
    main()