-- 2,655 distinct breed strings, hand typed. wanted cortex ai_classify here but it's blocked on trial accounts, so rules it is.
--
-- "bully adjacent" = looks blocky without carrying the label. rottweiler's in there on perception, not taxonomy.

CREATE OR REPLACE TABLE shelter.analytics.breed_groups AS
SELECT
  breed,
  CASE
    WHEN breed ILIKE '%pit bull%'
      OR breed ILIKE '%staffordshire%'
      THEN 'Pit Bull type'
    WHEN breed ILIKE '%boxer%'
      OR breed ILIKE '%bulldog%'
      OR breed ILIKE '%mastiff%'
      OR breed ILIKE '%cane corso%'
      OR breed ILIKE '%rottweiler%'
      OR breed ILIKE '%presa%'
      OR breed ILIKE '%dogo%'
      OR breed ILIKE '%bull terrier%'
      THEN 'Bully adjacent'
    ELSE 'Other'
  END AS breed_group
FROM (
  SELECT DISTINCT breed
  FROM shelter.analytics.dog_visits
  WHERE breed IS NOT NULL
);

-- checking nothing bully-shaped fell into Other
SELECT v.breed, COUNT(*) AS dogs
FROM shelter.analytics.dog_visits v
JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
WHERE g.breed_group = 'Other'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 30;
