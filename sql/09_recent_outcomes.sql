-- 15 months of completed stays under the new system.
--
-- the new system uses 26 outcome_status values where the old one used ~12, so they get normalised back to the old vocabulary before anything gets compared.

CREATE OR REPLACE VIEW shelter.analytics.recent_outcomes AS
SELECT
  animal_id,
  NULLIF(name, '') AS name,
  type,
  primary_breed AS breed,
  shelter.analytics.breed_group(primary_breed) AS breed_group,
  primary_color AS color,
  sex,
  TRY_TO_TIMESTAMP_NTZ(intake_date)  AS intake_ts,
  TRY_TO_TIMESTAMP_NTZ(outcome_date) AS outcome_ts,
  TRY_TO_NUMBER(days_in_shelter)     AS days_to_outcome,
  outcome_status,
  NULLIF(euthanasia_reason, '') AS euthanasia_reason,
  CASE
    WHEN outcome_status ILIKE 'Adopted%'                          THEN 'Adoption'
    WHEN outcome_status ILIKE 'Redemption%'
      OR outcome_status IN ('Reclaimed', 'Returned To Owner')     THEN 'Return to Owner'
    WHEN outcome_status ILIKE 'Transfer%'                         THEN 'Transfer'
    WHEN outcome_status ILIKE 'Euthan%'                           THEN 'Euthanasia'
    WHEN outcome_status ILIKE 'DOA%'
      OR outcome_status ILIKE 'Unassisted Death%'
      OR outcome_status ILIKE 'Crema%'
      OR outcome_status IN ('Interred')                           THEN 'Died'
    ELSE 'Other'
  END AS outcome_type
FROM shelter.raw.current_outcomes_raw
WHERE type IN ('Dog', 'Puppy');


-- does the finding hold on data it was never fitted to?
SELECT breed_group,
       COUNT(*) AS dogs,
       ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption') / COUNT(*), 1) AS pct_adopted,
       ROUND(MEDIAN(IFF(outcome_type = 'Adoption', days_to_outcome, NULL)), 1) AS median_days,
       ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption' AND days_to_outcome >= 30) / NULLIF(COUNT_IF(outcome_type = 'Adoption'), 0), 1) AS pct_over_30d
FROM shelter.analytics.recent_outcomes
WHERE days_to_outcome >= 0
GROUP BY 1
ORDER BY 5 DESC;


-- sanity: the old system's median adoption was 9 days, this looks a lot slower.
-- checking whether that's real or an artefact of how the new system counts.
SELECT outcome_type,
       COUNT(*) AS n,
       ROUND(MEDIAN(days_to_outcome), 1) AS median_days,
       ROUND(AVG(days_to_outcome), 1)    AS mean_days
FROM shelter.analytics.recent_outcomes
WHERE days_to_outcome >= 0
GROUP BY 1
ORDER BY 2 DESC;
