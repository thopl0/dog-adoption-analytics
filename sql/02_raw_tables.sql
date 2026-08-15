-- austin open data, no auth needed:
--   https://data.austintexas.gov/api/views/wter-evkm/rows.csv?accessType=DOWNLOAD  (intakes,  173,812)
--   https://data.austintexas.gov/api/views/9t4d-g238/rows.csv?accessType=DOWNLOAD  (outcomes, 173,775)

CREATE OR REPLACE TABLE shelter.raw.intakes_raw (
  animal_id        VARCHAR,
  name             VARCHAR,
  datetime_str     VARCHAR,
  monthyear        VARCHAR,
  found_location   VARCHAR,
  intake_type      VARCHAR,
  intake_condition VARCHAR,
  animal_type      VARCHAR,
  sex_upon_intake  VARCHAR,
  age_upon_intake  VARCHAR,
  breed            VARCHAR,
  color            VARCHAR
);

-- date_of_birth sits at column 2 here, intakes doesn't have it at all
CREATE OR REPLACE TABLE shelter.raw.outcomes_raw (
  animal_id        VARCHAR,
  date_of_birth    VARCHAR,
  name             VARCHAR,
  datetime_str     VARCHAR,
  monthyear        VARCHAR,
  outcome_type     VARCHAR,
  outcome_subtype  VARCHAR,
  animal_type      VARCHAR,
  sex_upon_outcome VARCHAR,
  age_upon_outcome VARCHAR,
  breed            VARCHAR,
  color            VARCHAR
);

-- loaded through snowsight with header = skip first line.
-- if outcomes comes back 173,776 the header snuck in as a row
SELECT 'intakes'  AS t, COUNT(*) FROM shelter.raw.intakes_raw
UNION ALL
SELECT 'outcomes' AS t, COUNT(*) FROM shelter.raw.outcomes_raw;
