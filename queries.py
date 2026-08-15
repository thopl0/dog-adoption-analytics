BREED_GROUPS = ["Other", "Bully adjacent", "Pit Bull type"]
CODED_COLOURS = ["Blue", "Black Brindle", "Brown Brindle", "Fawn"]

TREND = """
WITH h AS (SELECT YEAR(v.intake_ts) AS yr, g.breed_group, v.days_to_outcome, v.outcome_type
           FROM shelter.analytics.dog_visits v JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
           WHERE v.days_to_outcome >= 0),
     r AS (SELECT YEAR(intake_ts) AS yr, breed_group, days_to_outcome, outcome_type
           FROM shelter.analytics.recent_outcomes WHERE days_to_outcome >= 0),
     a AS (SELECT * FROM h UNION ALL SELECT * FROM r)
SELECT yr, breed_group, COUNT(*) AS dogs,
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1) AS median_days,
       ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1) AS pct_over_30d,
       ROUND(100.0*COUNT_IF(outcome_type='Adoption')/COUNT(*),1) AS pct_adopted
FROM a WHERE yr < YEAR(CURRENT_DATE()) GROUP BY 1,2 HAVING COUNT(*) >= 50 ORDER BY 1,2
"""

CUTS = """
WITH d AS (
  SELECT v.*, g.breed_group, SPLIT_PART(v.color,'/',1) AS primary_color,
         CASE WHEN v.age_days_at_intake < 365 THEN 'Under 1 year'
              WHEN v.age_days_at_intake < 1095 THEN '1 to 3 years'
              WHEN v.age_days_at_intake < 2555 THEN '3 to 7 years'
              WHEN v.age_days_at_intake IS NOT NULL THEN '7 years and up' END AS age_band
  FROM shelter.analytics.dog_visits v JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
  WHERE v.days_to_outcome >= 0
)
SELECT 'Breed group' AS cut, breed_group AS bucket, COUNT(*) AS dogs,
       ROUND(100.0*COUNT_IF(outcome_type='Adoption')/COUNT(*),1) AS pct_adopted,
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1) AS median_days,
       ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1) AS pct_over_30d
FROM d GROUP BY 2
UNION ALL SELECT 'Coat colour', primary_color, COUNT(*), ROUND(100.0*COUNT_IF(outcome_type='Adoption')/COUNT(*),1),
  ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1),
  ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1)
FROM d GROUP BY 2 HAVING COUNT(*) >= 500
UNION ALL SELECT 'Age on arrival', age_band, COUNT(*), ROUND(100.0*COUNT_IF(outcome_type='Adoption')/COUNT(*),1),
  ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1),
  ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1)
FROM d WHERE age_band IS NOT NULL GROUP BY 2
UNION ALL SELECT 'Condition on arrival', intake_condition, COUNT(*), ROUND(100.0*COUNT_IF(outcome_type='Adoption')/COUNT(*),1),
  ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1),
  ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1)
FROM d GROUP BY 2 HAVING COUNT(*) >= 300
UNION ALL SELECT 'How they arrived', intake_type, COUNT(*), ROUND(100.0*COUNT_IF(outcome_type='Adoption')/COUNT(*),1),
  ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1),
  ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1)
FROM d GROUP BY 2 HAVING COUNT(*) >= 300
"""

COLOURS = """
WITH d AS (
  SELECT *, SPLIT_PART(color,'/',1) AS primary_color,
         (breed ILIKE '%pit bull%' OR breed ILIKE '%staffordshire%' OR breed ILIKE '%bull terrier%' OR breed ILIKE '%american bulldog%') AS is_bully
  FROM shelter.analytics.dog_visits WHERE days_to_outcome >= 0
)
SELECT primary_color, COUNT(*) AS dogs,
       ROUND(100.0*COUNT_IF(is_bully)/COUNT(*),1) AS pct_bully,
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)),1) AS median_days,
       ROUND(100.0*COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30)/NULLIF(COUNT_IF(outcome_type='Adoption'),0),1) AS pct_over_30d
FROM d GROUP BY 1 HAVING COUNT(*) >= 500
"""

SURVIVAL = """
SELECT g.breed_group, t.day,
       ROUND(100.0 * COUNT_IF(v.days_to_outcome > t.day) / COUNT(*), 1) AS pct_still_there
FROM shelter.analytics.dog_visits v
JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
CROSS JOIN (SELECT seq4() * 5 AS day FROM TABLE(GENERATOR(ROWCOUNT => 25))) t
WHERE v.days_to_outcome >= 0 GROUP BY 1, 2
"""

ERA_CHECK = """
SELECT outcome_type, '2013-2025' AS era, ROUND(MEDIAN(days_to_outcome),1) AS median_days
FROM shelter.analytics.dog_visits
WHERE days_to_outcome >= 0 AND outcome_type IN ('Adoption','Transfer','Return to Owner') GROUP BY 1
UNION ALL SELECT outcome_type, '2025-now', ROUND(MEDIAN(days_to_outcome),1)
FROM shelter.analytics.recent_outcomes
WHERE days_to_outcome >= 0 AND outcome_type IN ('Adoption','Transfer','Return to Owner') GROUP BY 1
"""

LIVE_STATS = """
SELECT breed_group, COUNT(*) AS dogs, ROUND(AVG(days_waiting), 1) AS avg_days_waiting
FROM shelter.analytics.current_dogs GROUP BY 1
"""

ROSTER = """
SELECT animal_id, name, breed, breed_group, type, color, sex, age_years, days_waiting, intake_type
FROM shelter.analytics.current_dogs ORDER BY days_waiting DESC
"""

REPEATS = """
SELECT ROUND(100.0*COUNT_IF(visit_no>1)/COUNT(*),1) AS pct_repeat, MAX(visit_no) AS most_visits
FROM shelter.analytics.dog_visits
"""
