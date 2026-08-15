"""pulls austin's live feeds into snowflake. same shelter as the historical data, different
software since may 2025 so the schema doesn't match and these land in their own tables.

run from the project root:  python3 scripts/load_current.py
"""

import pathlib
import tomllib

import pandas as pd
import requests
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas

FEEDS = {
    "CURRENT_INTAKES_RAW": "pyqf-r2dc",
    "CURRENT_OUTCOMES_RAW": "gsvs-ypi7",
}

ROOT = pathlib.Path(__file__).parent.parent
cfg = dict(tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text())["connections"]["snowflake"])
cfg.pop("paramstyle", None)
cfg["schema"] = "RAW"


def fetch(dataset):
    rows, offset = [], 0
    while True:
        r = requests.get(
            f"https://data.austintexas.gov/resource/{dataset}.json",
            params={"$limit": 50000, "$offset": offset},
            timeout=90,
        )
        r.raise_for_status()
        page = r.json()
        rows += page
        if len(page) < 50000:
            return rows
        offset += 50000


conn = connect(**cfg)
for table, dataset in FEEDS.items():
    rows = fetch(dataset)
    df = pd.json_normalize(rows)
    df.columns = [c.upper() for c in df.columns]
    df = df.astype(str).replace({"nan": None, "None": None})
    ok, _, n, _ = write_pandas(conn, df, table, auto_create_table=True, overwrite=True, quote_identifiers=False)
    print(f"{table:<24} {n:>7,} rows from {dataset}  ok={ok}")
conn.close()
