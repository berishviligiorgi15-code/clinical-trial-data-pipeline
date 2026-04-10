-- 1. Trials by study type and phase
SELECT
    study_type,
    phase,
    COUNT(*) AS trial_count
FROM studies
GROUP BY study_type, phase
ORDER BY trial_count DESC;


-- 2. Most common conditions
SELECT
    c.condition_name,
    COUNT(*) AS study_count
FROM study_conditions sc
JOIN conditions c
    ON sc.condition_id = c.condition_id
GROUP BY c.condition_name
ORDER BY study_count DESC
LIMIT 20;


-- 3. Interventions with highest completion counts and rates
SELECT
    i.intervention_name,
    COUNT(*) AS total_trials,
    COUNT(*) FILTER (WHERE s.overall_status = 'COMPLETED') AS completed_trials,
    ROUND(
        COUNT(*) FILTER (WHERE s.overall_status = 'COMPLETED')::numeric
        / NULLIF(COUNT(*), 0),
        4
    ) AS completion_rate
FROM study_interventions si
JOIN interventions i
    ON si.intervention_id = i.intervention_id
JOIN studies s
    ON si.study_id = s.study_id
GROUP BY i.intervention_name
HAVING COUNT(*) >= 5
ORDER BY completion_rate DESC, total_trials DESC
LIMIT 20;


-- 4. Organization distribution
SELECT
    organization_class,
    COUNT(*) AS trial_count
FROM studies
GROUP BY organization_class
ORDER BY trial_count DESC;


-- 5. Study timeline by start year
SELECT
    EXTRACT(YEAR FROM start_date) AS start_year,
    COUNT(*) AS trial_count
FROM studies
WHERE start_date IS NOT NULL
GROUP BY EXTRACT(YEAR FROM start_date)
ORDER BY start_year;