-- if the visit numbering is off every duration comes out wrong but still looks believable, so check before building on it

SELECT COUNT(*)                     AS visits,
       COUNT(outcome_ts)            AS resolved,
       COUNT(*) - COUNT(outcome_ts) AS no_outcome
FROM shelter.analytics.dog_visits;


-- 89 rows, ignorable
SELECT COUNT(*) AS backwards
FROM shelter.analytics.dog_visits
WHERE days_to_outcome < 0;


-- the real check: return to owner should come out way faster than adoption. if those two blur together the pairing is broken.
SELECT outcome_type,
       COUNT(*)                          AS n,
       ROUND(MEDIAN(days_to_outcome), 1) AS median_days
FROM shelter.analytics.dog_visits
GROUP BY 1
ORDER BY 2 DESC;
