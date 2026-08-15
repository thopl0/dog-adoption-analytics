"""rebuilds every raw table from austin's api. run this instead of the upload wizard.

  python3 scripts/load_all.py
"""

import pathlib
import sys
import tomllib

import pandas as pd
import requests
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas

FEEDS = {
    "INTAKES_RAW": "wter-evkm",
    "OUTCOMES_RAW": "9t4d-g238",
    "CURRENT_INTAKES_RAW": "pyqf-r2dc",
    "CURRENT_OUTCOMES_RAW": "gsvs-ypi7",
}
PAGE = 50000

ROOT = pathlib.Path(__file__).parent.parent
cfg = dict(tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text())["connections"]["snowflake"])
cfg.pop("paramstyle", None)
cfg["schema"] = "RAW"


def fetch(dataset):
    rows, offset = [], 0
    while True:
        r = requests.get(f"https://data.austintexas.gov/resource/{dataset}.json",
                         params={"$limit": PAGE, "$offset": offset}, timeout=120)
        r.raise_for_status()
        page = r.json()
        rows += page
        sys.stdout.write(f"\r  {dataset}: {len(rows):,} rows")
        sys.stdout.flush()
        if len(page) < PAGE:
            print()
            return rows
        offset += PAGE


conn = connect(**cfg)
cur = conn.cursor()
for stmt in ("CREATE DATABASE IF NOT EXISTS SHELTER",
             "CREATE SCHEMA IF NOT EXISTS SHELTER.RAW",
             "CREATE SCHEMA IF NOT EXISTS SHELTER.ANALYTICS",
             "USE SCHEMA SHELTER.RAW"):
    cur.execute(stmt)

for table, dataset in FEEDS.items():
    df = pd.json_normalize(fetch(dataset))
    # the views expect datetime_str; the api calls it datetime
    df = df.rename(columns={"datetime": "datetime_str"})
    df.columns = [c.upper() for c in df.columns]
    df = df.astype(str).replace({"nan": None, "None": None})
    ok, _, n, _ = write_pandas(conn, df, table, database="SHELTER", schema="RAW",
                               auto_create_table=True, overwrite=True, quote_identifiers=False)
    print(f"  -> {table} {n:,} rows, ok={ok}\n")
conn.close()
print("done. now run sql/03, 04, 05, 08, 09 in a worksheet.")
