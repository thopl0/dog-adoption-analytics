-- median adoption is 9 days so medians alone don't say much, pct_over_30d is the one that matters. 
-- keeping pct_adopted next to it, otherwise you're only looking at dogs that made it and hidng the transfers and euthanasias.


-- 1. wait time by coat colour
WITH d AS (
  SELECT *, SPLIT_PART(color, '/', 1) AS primary_color
  FROM shelter.analytics.dog_visits
  WHERE days_to_outcome >= 0
)
SELECT
  primary_color,
  COUNT(*) AS dogs,
  ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption') / COUNT(*), 1) AS pct_adopted,
  ROUND(MEDIAN(IFF(outcome_type = 'Adoption', days_to_outcome, NULL)), 1) AS median_days,
  ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption' AND days_to_outcome >= 30) / NULLIF(COUNT_IF(outcome_type = 'Adoption'), 0), 1) AS pct_over_30d
FROM d
GROUP BY 1
HAVING COUNT(*) >= 500
ORDER BY pct_over_30d DESC;


-- 2. same thing but with % pit bull per colour, to see if colour is just standing in for breed
WITH d AS (
  SELECT *,
         SPLIT_PART(color, '/', 1) AS primary_color,
         (breed ILIKE '%pit bull%' OR breed ILIKE '%staffordshire%' OR breed ILIKE '%bull terrier%' OR breed ILIKE '%american bulldog%') AS is_bully
  FROM shelter.analytics.dog_visits
  WHERE days_to_outcome >= 0
)
SELECT
  primary_color,
  COUNT(*) AS dogs,
  ROUND(100.0 * COUNT_IF(is_bully) / COUNT(*), 1) AS pct_bully,
  ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption' AND days_to_outcome >= 30) / NULLIF(COUNT_IF(outcome_type = 'Adoption'), 0), 1) AS pct_over_30d
FROM d
GROUP BY 1
HAVING COUNT(*) >= 500
ORDER BY pct_over_30d DESC;


-- 3. first attempt at splitting label from looks, using colour as the stand-in for looks. 04 in the findings below replaces this, keeping it as the before.
WITH d AS (
  SELECT
    outcome_type,
    days_to_outcome,
    SPLIT_PART(color, '/', 1) AS primary_color,
    CASE WHEN breed ILIKE '%pit bull%' OR breed ILIKE '%staffordshire%' OR breed ILIKE '%bull terrier%' OR breed ILIKE '%american bulldog%' THEN 'bully' ELSE 'not_bully' END AS breed_group
  FROM shelter.analytics.dog_visits
  WHERE days_to_outcome >= 0
)
SELECT
  breed_group,
  CASE WHEN primary_color IN ('Blue','Black Brindle','Brown Brindle','Fawn') THEN 'bully_colour' ELSE 'other_colour' END AS colour_group,
  COUNT(*) AS dogs,
  ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption') / COUNT(*), 1) AS pct_adopted,
  ROUND(MEDIAN(IFF(outcome_type = 'Adoption', days_to_outcome, NULL)), 1) AS median_days,
  ROUND(100.0 * COUNT_IF(outcome_type = 'Adoption' AND days_to_outcome >= 30) / NULLIF(COUNT_IF(outcome_type = 'Adoption'), 0), 1) AS pct_over_30d
FROM d
GROUP BY 1, 2
ORDER BY 1, 2;


-- 4. the main one
SELECT
  g.breed_group,
  COUNT(*) AS dogs,
  ROUND(100.0 * COUNT_IF(v.outcome_type = 'Adoption') / COUNT(*), 1) AS pct_adopted,
  ROUND(MEDIAN(IFF(v.outcome_type = 'Adoption', v.days_to_outcome, NULL)), 1) AS median_days,
  ROUND(100.0 * COUNT_IF(v.outcome_type = 'Adoption' AND v.days_to_outcome >= 30) / NULLIF(COUNT_IF(v.outcome_type = 'Adoption'), 0), 1) AS pct_over_30d
FROM shelter.analytics.dog_visits v
JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
WHERE v.days_to_outcome >= 0
GROUP BY 1
ORDER BY 5 DESC;
