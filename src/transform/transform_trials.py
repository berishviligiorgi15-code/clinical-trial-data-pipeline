from src.db.connection import get_connection


SQL_STATEMENTS = [
    """
    TRUNCATE TABLE
        study_mesh_terms,
        mesh_terms,
        outcomes,
        study_interventions,
        interventions,
        study_conditions,
        conditions,
        studies
    RESTART IDENTITY CASCADE;
    """,
    """
    INSERT INTO studies (
        source_row_num,
        study_business_key,
        organization_full_name,
        organization_class,
        responsible_party,
        brief_title,
        full_title,
        overall_status,
        standard_age,
        primary_purpose,
        study_type,
        phase,
        intervention_description
    )
    SELECT
        s.row_num,
        md5(
            lower(trim(coalesce(s.brief_title, ''))) || '||' ||
            lower(trim(coalesce(s.organization_full_name, ''))) || '||' ||
            lower(trim(coalesce(s.start_date_raw, '')))
        ) AS study_business_key,
        NULLIF(trim(s.organization_full_name), ''),
        CASE
            WHEN lower(trim(coalesce(s.organization_class, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE upper(replace(trim(s.organization_class), ' ', '_'))
        END,
        CASE
            WHEN lower(trim(coalesce(s.responsible_party, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE upper(replace(trim(s.responsible_party), ' ', '_'))
        END,
        trim(s.brief_title),
        CASE
            WHEN lower(trim(coalesce(s.full_title, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE trim(s.full_title)
        END,
        CASE
            WHEN lower(trim(coalesce(s.overall_status, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE upper(replace(trim(s.overall_status), ' ', '_'))
        END,
        CASE
            WHEN lower(trim(coalesce(s.standard_age_raw, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE trim(s.standard_age_raw)
        END,
        CASE
            WHEN lower(trim(coalesce(s.primary_purpose, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE upper(replace(trim(s.primary_purpose), ' ', '_'))
        END,
        CASE
            WHEN lower(trim(coalesce(s.study_type, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE upper(replace(trim(s.study_type), ' ', '_'))
        END,
        CASE
            WHEN lower(trim(coalesce(s.phases_raw, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE upper(replace(trim(s.phases_raw), ' ', '_'))
        END,
        CASE
            WHEN lower(trim(coalesce(s.intervention_description_raw, ''))) IN ('', 'unknown', 'na', 'n/a', 'none', 'null') THEN NULL
            ELSE regexp_replace(trim(s.intervention_description_raw), '\\s+', ' ', 'g')
        END
    FROM stg_clinical_trials s
    WHERE lower(trim(coalesce(s.brief_title, ''))) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT (study_business_key) DO NOTHING;
    """,
    """
    UPDATE studies st
    SET
        start_date = CASE
            WHEN s.start_date_raw ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$'
                THEN to_date(trim(s.start_date_raw), 'MM/DD/YY')
            WHEN s.start_date_raw ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$'
                THEN to_date(trim(s.start_date_raw), 'MM/DD/YYYY')
            WHEN s.start_date_raw ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                THEN to_date(trim(s.start_date_raw), 'YYYY-MM-DD')
            WHEN s.start_date_raw ~ '^[0-9]{4}-[0-9]{2}$'
                THEN to_date(trim(s.start_date_raw) || '-01', 'YYYY-MM-DD')
            WHEN s.start_date_raw ~ '^[0-9]{4}$'
                THEN to_date(trim(s.start_date_raw) || '-01-01', 'YYYY-MM-DD')
            ELSE NULL
        END,
        start_date_precision = CASE
            WHEN s.start_date_raw ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$' THEN 'day'
            WHEN s.start_date_raw ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$' THEN 'day'
            WHEN s.start_date_raw ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN 'day'
            WHEN s.start_date_raw ~ '^[0-9]{4}-[0-9]{2}$' THEN 'month'
            WHEN s.start_date_raw ~ '^[0-9]{4}$' THEN 'year'
            ELSE NULL
        END
    FROM stg_clinical_trials s
    WHERE st.study_business_key = md5(
        lower(trim(coalesce(s.brief_title, ''))) || '||' ||
        lower(trim(coalesce(s.organization_full_name, ''))) || '||' ||
        lower(trim(coalesce(s.start_date_raw, '')))
    );
    """,
    """
    INSERT INTO conditions (condition_name)
    SELECT DISTINCT item
    FROM (
        SELECT trim(regexp_split_to_table(coalesce(conditions_raw, ''), ',')) AS item
        FROM stg_clinical_trials
    ) t
    WHERE lower(item) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT (condition_name) DO NOTHING;
    """,
    """
    INSERT INTO study_conditions (study_id, condition_id)
    SELECT DISTINCT
        st.study_id,
        c.condition_id
    FROM stg_clinical_trials s
    JOIN studies st
      ON st.study_business_key = md5(
            lower(trim(coalesce(s.brief_title, ''))) || '||' ||
            lower(trim(coalesce(s.organization_full_name, ''))) || '||' ||
            lower(trim(coalesce(s.start_date_raw, '')))
         )
    CROSS JOIN LATERAL regexp_split_to_table(coalesce(s.conditions_raw, ''), ',') AS raw_item
    JOIN conditions c
      ON c.condition_name = trim(raw_item)
    WHERE lower(trim(raw_item)) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT DO NOTHING;
    """,
    """
    INSERT INTO interventions (intervention_name)
    SELECT DISTINCT item
    FROM (
        SELECT trim(regexp_split_to_table(coalesce(interventions_raw, ''), ',')) AS item
        FROM stg_clinical_trials
    ) t
    WHERE lower(item) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT (intervention_name) DO NOTHING;
    """,
    """
    INSERT INTO study_interventions (study_id, intervention_id)
    SELECT DISTINCT
        st.study_id,
        i.intervention_id
    FROM stg_clinical_trials s
    JOIN studies st
      ON st.study_business_key = md5(
            lower(trim(coalesce(s.brief_title, ''))) || '||' ||
            lower(trim(coalesce(s.organization_full_name, ''))) || '||' ||
            lower(trim(coalesce(s.start_date_raw, '')))
         )
    CROSS JOIN LATERAL regexp_split_to_table(coalesce(s.interventions_raw, ''), ',') AS raw_item
    JOIN interventions i
      ON i.intervention_name = trim(raw_item)
    WHERE lower(trim(raw_item)) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT DO NOTHING;
    """,
    """
    INSERT INTO outcomes (study_id, outcome_measure)
    SELECT
        st.study_id,
        regexp_replace(trim(s.outcome_measure_raw), '\\s+', ' ', 'g')
    FROM stg_clinical_trials s
    JOIN studies st
      ON st.study_business_key = md5(
            lower(trim(coalesce(s.brief_title, ''))) || '||' ||
            lower(trim(coalesce(s.organization_full_name, ''))) || '||' ||
            lower(trim(coalesce(s.start_date_raw, '')))
         )
    WHERE lower(trim(coalesce(s.outcome_measure_raw, ''))) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null');
    """,
    """
    INSERT INTO mesh_terms (mesh_term)
    SELECT DISTINCT item
    FROM (
        SELECT trim(regexp_split_to_table(coalesce(medical_subject_headings_raw, ''), ',')) AS item
        FROM stg_clinical_trials
    ) t
    WHERE lower(item) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT (mesh_term) DO NOTHING;
    """,
    """
    INSERT INTO study_mesh_terms (study_id, mesh_term_id)
    SELECT DISTINCT
        st.study_id,
        m.mesh_term_id
    FROM stg_clinical_trials s
    JOIN studies st
      ON st.study_business_key = md5(
            lower(trim(coalesce(s.brief_title, ''))) || '||' ||
            lower(trim(coalesce(s.organization_full_name, ''))) || '||' ||
            lower(trim(coalesce(s.start_date_raw, '')))
         )
    CROSS JOIN LATERAL regexp_split_to_table(coalesce(s.medical_subject_headings_raw, ''), ',') AS raw_item
    JOIN mesh_terms m
      ON m.mesh_term = trim(raw_item)
    WHERE lower(trim(raw_item)) NOT IN ('', 'unknown', 'na', 'n/a', 'none', 'null')
    ON CONFLICT DO NOTHING;
    """,
]


def transform_and_load():
    conn = get_connection()
    cur = conn.cursor()

    try:
        for i, statement in enumerate(SQL_STATEMENTS, start=1):
            print(f"Running step {i}/{len(SQL_STATEMENTS)}...")
            cur.execute(statement)
            conn.commit()

        print("Transformation and core table load completed successfully.")

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    transform_and_load()