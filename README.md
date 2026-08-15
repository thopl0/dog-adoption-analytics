# The pit bull penalty

Thirteen years of Austin Animal Center records in Snowflake, and a Streamlit app on top of them, asking what it costs a dog to look like a pit bull.

**[Live app](https://dog-adoption-analytics.streamlit.app/)** · **[Write-up](https://dev.to/thopl0/380000-shelter-records-what-it-costs-a-dog-to-just-look-like-a-pit-bull-3ibc)**

## The finding

The question this started from was whether the case for banning pit bulls holds up. It can't be settled from the numbers people quote at each other, because breed on a bite report is whoever filled the form in guessing by eye. In [Olson and Levy's study](https://www.sciencedirect.com/science/article/pii/S109002331500310X), 16 shelter staff identified 120 dogs and then the dogs were DNA tested. DNA found 25 pit bull types. The staff called 62.

What Austin's records can measure is what that guessing costs.

Black dog syndrome does not show up at all. Black dogs are the largest group in the data, 24,546 of them, adopted more often than white dogs, and eighth of seventeen colours on wait time. The colours that _are_ slow (blue, fawn, and the two brindles) are the words people use when describing a pit bull. Blue dogs are 81.8% pit bull.

Grouping dogs by how much they look the part, the wait doubles at each step:

| breed group    | dogs   | adopted | median days | waited over a month |
| -------------- | ------ | ------- | ----------- | ------------------- |
| Other          | 70,936 | 51.5%   | 8           | 21.1%               |
| Bully adjacent | 5,198  | 45.7%   | 14          | 33.8%               |
| Pit Bull type  | 17,831 | 46.0%   | 28          | 48.9%               |

**`Bully adjacent` is the row that matters.** Boxers, cane corsos, bullmastiffs, rottweilers. Nobody wrote pit bull on their paperwork. They only look like one, and it costs them about 46% of the full penalty. It is the same visual identification that fills in the breed box on a bite report, with a number attached.

Three checks on that result:

- **It replicates out of sample.** 23 / 38.5 / 54 days across 6,052 stays under Austin's new record system, a different pipeline with a different schema that the analysis was never fitted to.
- **It is not a counting change.** Transfers held at 5 days across the system switch while adoption went from 9 days to 28. Only the outcome that needs a member of the public to choose a dog moved.
- **It is not the economy.** Correlation between Austin metro unemployment and the gap between breed groups is -0.02 across 123 non-pandemic months.

## How it works

```
shelter.raw            untouched source data, every column VARCHAR
  intakes_raw            historical intakes, 173,812
  outcomes_raw           historical outcomes, 173,775
  current_intakes_raw    live feed
  current_outcomes_raw   live feed
shelter.analytics      everything typed and derived
  intakes, outcomes    typed views over raw
  visits               TABLE, one row per shelter stay, with days_to_outcome
  dog_visits           view, visits filtered to dogs
  breed_groups         TABLE, one row per distinct breed string
  breed_group(str)     UDF, the same rules callable on live rows
  current_dogs         view, dogs in the shelter right now
  recent_outcomes      view, new-system outcomes normalised to the old vocabulary
```

Three things in here are worth reading the SQL for.

**Pairing arrivals to departures** (`sql/04_visits.sql`). `animal_id` is not unique, because about one visit in five is a dog coming back and one animal returned eleven times. Joining on the id alone gives every arrival crossed with every departure. Each side is numbered chronologically per animal with `ROW_NUMBER()` and joined on `(animal_id, visit_no)`, with a `LEFT JOIN` so dogs that never left are kept.

**Breed grouping** (`sql/05_breed_groups.sql`) is a rule set over 2,655 hand-typed breed strings, not a model. The point of this project is an argument about bias, so the classifier needs to be readable line by line. `sql/08` re-encodes the same rules as a UDF, because the live feed has breed strings that never appear historically and a join to the lookup table would drop them silently.

**Gemini never writes SQL.** It converts a sentence into JSON, `ai.py` validates every field against known values, and free text reaches Snowflake as a bound parameter. The app shows both the JSON and the generated query.

## Running it

Python 3.12. Newer versions have no wheels for the Snowflake connector.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`, which is gitignored:

```toml
[connections.snowflake]
account   = "your-org-your-account"
user      = "..."
password  = "..."
role      = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
database  = "SHELTER"
schema    = "ANALYTICS"
paramstyle = "qmark"   # required, the connector will not bind %s here

[gemini]
api_key = "..."
model   = "gemini-2.5-flash"
```

Build the warehouse. The loader creates the database and schemas itself, so `sql/01` is not a prerequisite:

```bash
python scripts/load_all.py     # all four feeds from the Socrata API, ~380,000 rows
```

Then run `sql/03`, `04`, `05`, `08`, `09` in that order. Skip `02` (superseded by the loader, kept as a record of the raw schema) and `06`/`07` (sanity checks and analysis, not build steps).

Check it built correctly:

```sql
SELECT COUNT(*) FROM shelter.analytics.dog_visits;      -- 94,608
SELECT COUNT(*) FROM shelter.analytics.current_dogs;    -- ~600, live, it drifts
SELECT COUNT(*) FROM shelter.analytics.recent_outcomes; -- ~6,050, also live
```

```bash
streamlit run app.py
```

The app does not need the Marketplace listing. That was used for one analysis step, ruling out a link between the local economy and adoption speed, by attaching `GZTSZ290BV255` (Snowflake Public Data, free) and joining BLS unemployment for the Austin metro on year-month.

## Layout

```
app.py           the page, and nothing else
ui.py            palette, CSS, layout helpers, header and footer
queries.py       every SQL string used by the app
db.py            connection and q(), which casts Snowflake Decimal to float
ai.py            Gemini prompt, model fallback, parse_request, build_search
sql/             01-07 historical build, 08 current dogs, 09 recent outcomes
scripts/         load_all.py rebuilds the raw layer, load_current.py refreshes the live feeds
```

## Data

All City of Austin open data via Socrata, no auth required.

| dataset              | id          | rows    |
| -------------------- | ----------- | ------- |
| Intakes, historical  | `wter-evkm` | 173,812 |
| Outcomes, historical | `9t4d-g238` | 173,775 |
| Intakes, live        | `pyqf-r2dc` | ~16,300 |
| Outcomes, live       | `gsvs-ypi7` | ~16,100 |

The two live feeds come from a different system with completely different schemas. They are loaded separately and only stitched at the analytics layer. The live intake feed splits `Dog` and `Puppy` into separate `type` values, so filtering on `= 'Dog'` silently drops puppies.

## What I would argue with

Austin's `breed` column is shelter staff recording what they think a dog is, which is the same visual identification this project is about. The `Pit Bull type` group is dogs that people called pit bulls. This measures what happens to a dog that gets seen a certain way, not anything genetic.

None of it says whether pit bulls are dangerous. That question is in the write-up, along with why the data everybody argues over cannot answer it.

Rottweilers are in the middle group on how people react to them, not on taxonomy. Anatolian Shepherds and Great Pyrenees were left in `Other` rather than moved, which would have helped the result.

89 rows of 93,965 have a departure recorded before the arrival, which is what hand-entered municipal data looks like. They are filtered and nothing moves.

## Licence

Data is City of Austin open data, CC0. Code is MIT.
