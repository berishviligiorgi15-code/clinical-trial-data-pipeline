CREATE TABLE IF NOT EXISTS stg_clinical_trials (
    row_num BIGINT,
    organization_full_name TEXT,
    organization_class TEXT,
    responsible_party TEXT,
    brief_title TEXT,
    full_title TEXT,
    overall_status TEXT,
    start_date_raw TEXT,
    standard_age_raw TEXT,
    conditions_raw TEXT,
    primary_purpose TEXT,
    interventions_raw TEXT,
    intervention_description_raw TEXT,
    study_type TEXT,
    phases_raw TEXT,
    outcome_measure_raw TEXT,
    medical_subject_headings_raw TEXT,
    source_file_name TEXT NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS studies (
    study_id BIGSERIAL PRIMARY KEY,
    source_row_num BIGINT,
    study_business_key TEXT NOT NULL UNIQUE,
    organization_full_name TEXT,
    organization_class TEXT,
    responsible_party TEXT,
    brief_title TEXT NOT NULL,
    full_title TEXT,
    overall_status TEXT,
    start_date DATE,
    start_date_precision TEXT,
    standard_age TEXT,
    primary_purpose TEXT,
    study_type TEXT,
    phase TEXT,
    intervention_description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conditions (
    condition_id BIGSERIAL PRIMARY KEY,
    condition_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS study_conditions (
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    condition_id BIGINT NOT NULL REFERENCES conditions(condition_id) ON DELETE CASCADE,
    PRIMARY KEY (study_id, condition_id)
);

CREATE TABLE IF NOT EXISTS interventions (
    intervention_id BIGSERIAL PRIMARY KEY,
    intervention_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS study_interventions (
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    intervention_id BIGINT NOT NULL REFERENCES interventions(intervention_id) ON DELETE CASCADE,
    PRIMARY KEY (study_id, intervention_id)
);

CREATE TABLE IF NOT EXISTS outcomes (
    outcome_id BIGSERIAL PRIMARY KEY,
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    outcome_measure TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mesh_terms (
    mesh_term_id BIGSERIAL PRIMARY KEY,
    mesh_term TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS study_mesh_terms (
    study_id BIGINT NOT NULL REFERENCES studies(study_id) ON DELETE CASCADE,
    mesh_term_id BIGINT NOT NULL REFERENCES mesh_terms(mesh_term_id) ON DELETE CASCADE,
    PRIMARY KEY (study_id, mesh_term_id)
);

CREATE INDEX IF NOT EXISTS idx_studies_overall_status
    ON studies (overall_status);

CREATE INDEX IF NOT EXISTS idx_studies_study_type
    ON studies (study_type);

CREATE INDEX IF NOT EXISTS idx_studies_phase
    ON studies (phase);

CREATE INDEX IF NOT EXISTS idx_studies_start_date
    ON studies (start_date);

CREATE INDEX IF NOT EXISTS idx_studies_primary_purpose
    ON studies (primary_purpose);

CREATE INDEX IF NOT EXISTS idx_study_conditions_condition_id
    ON study_conditions (condition_id);

CREATE INDEX IF NOT EXISTS idx_study_interventions_intervention_id
    ON study_interventions (intervention_id);

CREATE INDEX IF NOT EXISTS idx_study_mesh_terms_mesh_term_id
    ON study_mesh_terms (mesh_term_id);

CREATE INDEX IF NOT EXISTS idx_outcomes_study_id
    ON outcomes (study_id);