-- animal_id isn't unique. same animal can have multiple records since they can come back to the shelter later. 
-- so joining on it alone crosses every intake with every outcome and numbering each side per animal and joining on (animal_id, visit_no) instead.

CREATE OR REPLACE TABLE shelter.analytics.visits AS
WITH i AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY animal_id ORDER BY intake_ts, intake_type) AS visit_no
  FROM shelter.analytics.intakes
),
o AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY animal_id ORDER BY outcome_ts, outcome_type) AS visit_no
  FROM shelter.analytics.outcomes
)
SELECT
  i.animal_id,
  i.visit_no,
  i.animal_type,
  i.name,
  i.breed,
  i.color,
  i.intake_ts,
  i.intake_type,
  i.intake_condition,
  i.found_location,
  i.sex_upon_intake,
  i.age_upon_intake,
  o.outcome_ts,
  o.outcome_type,
  o.outcome_subtype,
  o.dob,
  DATEDIFF('day', i.intake_ts, o.outcome_ts) AS days_to_outcome,
  -- age_upon_intake is text like "7 years", "1 week"
  CASE
    WHEN i.age_upon_intake ILIKE '%year%'  THEN TRY_TO_NUMBER(SPLIT_PART(i.age_upon_intake,' ',1)) * 365
    WHEN i.age_upon_intake ILIKE '%month%' THEN TRY_TO_NUMBER(SPLIT_PART(i.age_upon_intake,' ',1)) * 30
    WHEN i.age_upon_intake ILIKE '%week%'  THEN TRY_TO_NUMBER(SPLIT_PART(i.age_upon_intake,' ',1)) * 7
    WHEN i.age_upon_intake ILIKE '%day%'   THEN TRY_TO_NUMBER(SPLIT_PART(i.age_upon_intake,' ',1))
  END AS age_days_at_intake
FROM i
LEFT JOIN o
  ON  i.animal_id = o.animal_id
  AND i.visit_no  = o.visit_no;

CREATE OR REPLACE VIEW shelter.analytics.dog_visits AS
SELECT * FROM shelter.analytics.visits WHERE animal_type = 'Dog';
