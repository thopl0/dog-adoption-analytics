from decimal import Decimal

import streamlit as st

_conn = st.connection("snowflake")


def q(sql, **kw):
    df = _conn.query(sql, ttl=3600, **kw).copy()
    df.columns = df.columns.str.lower()
    for c in df.columns:
        if df[c].dtype == object and df[c].map(lambda v: isinstance(v, Decimal)).any():
            df[c] = df[c].astype(float)
    return df
