-- dogs sitting in the shelter right now. loaded by scripts/load_current.py from austin's post-may-2025 feeds, which are the same shelter on different software. 
-- schemas don't match the historical tables and animal_id changed format, so these never get merged.

-- same rules as 05, as a function so the live side can't drift from the historical side
CREATE OR REPLACE FUNCTION shelter.analytics.breed_group(breed VARCHAR)
RETURNS VARCHAR
AS
$$
  CASE
    WHEN breed ILIKE '%pit bull%' OR breed ILIKE '%staffordshire%' THEN 'Pit Bull type'
    WHEN breed ILIKE '%boxer%' OR breed ILIKE '%bulldog%' OR breed ILIKE '%mastiff%'
      OR breed ILIKE '%cane corso%' OR breed ILIKE '%rottweiler%' OR breed ILIKE '%presa%'
      OR breed ILIKE '%dogo%' OR breed ILIKE '%bull terrier%' THEN 'Bully adjacent'
    ELSE 'Other'
  END
$$;

CREATE OR REPLACE VIEW shelter.analytics.current_dogs AS
WITH i AS (
  SELECT animal_id,
         NULLIF(name_at_intake, '') AS name,
         type,
         primary_breed AS breed,
         NULLIF(primary_color, '') AS color,
         NULLIF(secondary_color, '') AS color2,
         sex,
         intake_health_condition AS condition,
         source_name AS intake_type,
         TRY_TO_TIMESTAMP_NTZ(source_date) AS intake_ts,
         TRY_TO_DATE(LEFT(date_of_birth, 10), 'YYYY-MM-DD') AS dob
  FROM shelter.raw.current_intakes_raw
  WHERE type IN ('Dog', 'Puppy')
)
SELECT i.*,
       shelter.analytics.breed_group(i.breed) AS breed_group,
       DATEDIFF('day', i.intake_ts, CURRENT_TIMESTAMP()) AS days_waiting,
       DATEDIFF('year', i.dob, CURRENT_DATE()) AS age_years
FROM i
WHERE NOT EXISTS (
  SELECT 1 FROM shelter.raw.current_outcomes_raw o
  WHERE o.animal_id = i.animal_id
    AND TRY_TO_TIMESTAMP_NTZ(o.outcome_date) >= i.intake_ts
);

SELECT breed_group, COUNT(*) AS dogs, ROUND(AVG(days_waiting), 1) AS avg_days_waiting
FROM shelter.analytics.current_dogs GROUP BY 1 ORDER BY 2 DESC;
