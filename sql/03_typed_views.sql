-- the two files timestamp differently for whatever reason:
--   intakes   10/01/2013 07:51:00 AM
--   outcomes  2013-12-02T00:00:00-05:00


CREATE OR REPLACE VIEW shelter.analytics.intakes AS
SELECT
  animal_id,
  animal_type,
  NULLIF(name,'') AS name,
  COALESCE(
    TRY_TO_TIMESTAMP_NTZ(datetime_str, 'MM/DD/YYYY HH12:MI:SS AM'),
    TRY_TO_TIMESTAMP_NTZ(REPLACE(LEFT(datetime_str, 19), 'T', ' '), 'YYYY-MM-DD HH24:MI:SS')
  ) AS intake_ts,
  found_location,
  intake_type,
  intake_condition,
  sex_upon_intake,
  age_upon_intake,
  breed,
  color
FROM shelter.raw.intakes_raw;

CREATE OR REPLACE VIEW shelter.analytics.outcomes AS
SELECT
  animal_id,
  animal_type,
  TRY_TO_DATE(date_of_birth, 'YYYY-MM-DD') AS dob,
  NULLIF(name,'') AS name,
  TRY_TO_TIMESTAMP_NTZ(REPLACE(LEFT(datetime_str, 19), 'T', ' '), 'YYYY-MM-DD HH24:MI:SS') AS outcome_ts,
  outcome_type,
  outcome_subtype,
  sex_upon_outcome,
  age_upon_outcome,
  breed,
  color
FROM shelter.raw.outcomes_raw;

-- came back 0
SELECT COUNT(*) AS unparsed FROM shelter.analytics.outcomes WHERE outcome_ts IS NULL;
