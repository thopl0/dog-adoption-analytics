from decimal import Decimal

import altair as alt
import streamlit as st

st.set_page_config(page_title="the pit bull penalty", layout="wide", initial_sidebar_state="collapsed")

SURFACE = "#fcfcfb"
MUTED = "#898781"
GRID = "#e6e5df"
RAMP = ["#86b6ef", "#2a78d6", "#104281"]
QUIET = "#cfcec6"
BLUE = "#2a78d6"

ORDER = ["Other", "Bully adjacent", "Pit Bull type"]
CODED = ["Blue", "Black Brindle", "Brown Brindle", "Fawn"]

METRICS = {
    "Waited over a month": ("pct_over_30d", "% of adopted dogs that took 30+ days"),
    "Median days to adoption": ("median_days", "days"),
    "Adoption rate": ("pct_adopted", "% of outcomes that were adoptions"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400&family=Inter:wght@400;500;600&display=swap');
.stApp { background: #fcfcfb; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1240px; padding-top: 1.6rem; padding-bottom: 5rem; }
html, body, [class*="css"], .stMarkdown { font-family: 'Inter', system-ui, sans-serif; }

.hd { display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; flex-wrap: wrap; }
h1.claim {
  font-family: 'Newsreader', Georgia, serif; font-weight: 400;
  font-size: clamp(1.9rem, 3.4vw, 2.7rem); line-height: 1.1; letter-spacing: -0.02em;
  color: #0b0b0b; margin: 0;
}
p.sub { font-size: 0.88rem; color: #898781; margin: 0.55rem 0 0 0; max-width: 46ch; line-height: 1.5; }

.stats { display: flex; gap: 0; border-top: 1px solid #e1e0d9; border-bottom: 1px solid #e1e0d9; margin: 1.5rem 0 0 0; }
.stat { flex: 1; padding: 0.95rem 0 1rem 0; }
.stat + .stat { border-left: 1px solid #e1e0d9; padding-left: 1.1rem; }
.stat .n { font-size: 2.15rem; font-weight: 500; line-height: 1; letter-spacing: -0.03em; color: #0b0b0b; }
.stat .n small { font-size: 0.85rem; font-weight: 400; color: #898781; margin-left: 0.25rem; letter-spacing: 0; }
.stat .k { font-size: 0.79rem; color: #52514e; margin-top: 0.38rem; display: flex; align-items: center; gap: 0.4rem; }
.swatch { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }

h2.sec { font-size: 1.02rem; font-weight: 600; color: #0b0b0b; margin: 2.4rem 0 0.15rem 0; letter-spacing: -0.01em; }
p.note { font-size: 0.83rem; line-height: 1.5; color: #898781; margin: 0.25rem 0 0.8rem 0; max-width: 78ch; }
p.read { font-size: 0.92rem; line-height: 1.6; color: #26251f; margin: 0.6rem 0 0 0; max-width: 70ch; }
p.read b { font-weight: 600; color: #0b0b0b; }

.stTextInput input { border-radius: 6px; border: 1px solid #dcdbd3; background: #fff; font-size: 0.95rem; }
div[data-baseweb="select"] > div { border-radius: 6px; border-color: #dcdbd3; background: #fff; }
div[data-testid="stExpander"] details { border: none; border-top: 1px solid #e1e0d9; border-radius: 0; }
div[data-testid="stExpander"] summary { font-size: 0.8rem; color: #898781; }
hr { border-color: #e1e0d9; margin: 2.2rem 0 0 0; }

.pill {
  display: inline-flex; align-items: center; gap: 0.42rem;
  border: 1px solid #dcdbd3; border-radius: 999px; padding: 0.3rem 0.7rem;
  font-size: 0.78rem; color: #52514e; background: #fff; white-space: nowrap;
}
.pill .dot { width: 6px; height: 6px; border-radius: 999px; background: #2a78d6; }
.foot {
  display: flex; flex-wrap: wrap; gap: 0.5rem 1.4rem; align-items: center;
  border-top: 1px solid #e1e0d9; margin-top: 2.6rem; padding-top: 1.1rem;
  font-size: 0.82rem; color: #898781;
}
.foot a { color: #2a78d6; text-decoration: none; }
.foot a:hover { text-decoration: underline; }

.src {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.74rem; color: #a3a19a; margin: 0.35rem 0 0 0;
}
.src .dot { width: 5px; height: 5px; border-radius: 999px; background: #86b6ef; flex: none; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

conn = st.connection("snowflake")


def q(sql, **kw):
    df = conn.query(sql, ttl=3600, **kw).copy()
    df.columns = df.columns.str.lower()
    # snowflake hands back NUMBER as Decimal, which won't do arithmetic with floats
    for c in df.columns:
        if df[c].dtype == object and df[c].map(lambda v: isinstance(v, Decimal)).any():
            df[c] = df[c].astype(float)
    return df


def sec(title, note=None):
    st.markdown(f'<h2 class="sec">{title}</h2>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<p class="note">{note}</p>', unsafe_allow_html=True)


def read(text):
    st.markdown(f'<p class="read">{text}</p>', unsafe_allow_html=True)


def src(what="Queried live from Snowflake"):
    st.markdown(f'<p class="src"><span class="dot"></span>{what}</p>', unsafe_allow_html=True)


def style(chart, height):
    return (
        chart.properties(height=height, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True, gridColor=GRID, gridWidth=1, domain=False, tickSize=0,
                        labelColor="#52514e", titleColor=MUTED, labelFontSize=14, titleFontSize=12,
                        labelPadding=10, titlePadding=16, labelFont="Inter", titleFont="Inter")
        .configure_legend(labelColor="#52514e", labelFont="Inter", labelFontSize=13,
                          symbolType="square", symbolSize=140)
        .configure_text(font="Inter")
    )


CUTS = """
WITH d AS (
  SELECT v.*, g.breed_group,
         SPLIT_PART(v.color, '/', 1) AS primary_color,
         CASE WHEN v.age_days_at_intake < 365      THEN 'Under 1 year'
              WHEN v.age_days_at_intake < 1095     THEN '1 to 3 years'
              WHEN v.age_days_at_intake < 2555     THEN '3 to 7 years'
              WHEN v.age_days_at_intake IS NOT NULL THEN '7 years and up' END AS age_band
  FROM shelter.analytics.dog_visits v
  JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
  WHERE v.days_to_outcome >= 0
)
SELECT 'Breed group' AS cut, breed_group AS bucket, COUNT(*) AS dogs,
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption') / COUNT(*), 1) AS pct_adopted,
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)), 1) AS median_days,
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30) / NULLIF(COUNT_IF(outcome_type='Adoption'),0), 1) AS pct_over_30d
FROM d GROUP BY 2
UNION ALL
SELECT 'Coat colour', primary_color, COUNT(*),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption') / COUNT(*), 1),
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)), 1),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30) / NULLIF(COUNT_IF(outcome_type='Adoption'),0), 1)
FROM d GROUP BY 2 HAVING COUNT(*) >= 500
UNION ALL
SELECT 'Age on arrival', age_band, COUNT(*),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption') / COUNT(*), 1),
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)), 1),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30) / NULLIF(COUNT_IF(outcome_type='Adoption'),0), 1)
FROM d WHERE age_band IS NOT NULL GROUP BY 2
UNION ALL
SELECT 'Condition on arrival', intake_condition, COUNT(*),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption') / COUNT(*), 1),
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)), 1),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30) / NULLIF(COUNT_IF(outcome_type='Adoption'),0), 1)
FROM d GROUP BY 2 HAVING COUNT(*) >= 300
UNION ALL
SELECT 'How they arrived', intake_type, COUNT(*),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption') / COUNT(*), 1),
       ROUND(MEDIAN(IFF(outcome_type='Adoption', days_to_outcome, NULL)), 1),
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30) / NULLIF(COUNT_IF(outcome_type='Adoption'),0), 1)
FROM d GROUP BY 2 HAVING COUNT(*) >= 300
"""

SCATTER = """
WITH d AS (
  SELECT *, SPLIT_PART(color, '/', 1) AS primary_color,
         (breed ILIKE '%pit bull%' OR breed ILIKE '%staffordshire%' OR breed ILIKE '%bull terrier%' OR breed ILIKE '%american bulldog%') AS is_bully
  FROM shelter.analytics.dog_visits WHERE days_to_outcome >= 0
)
SELECT primary_color, COUNT(*) AS dogs,
       ROUND(100.0 * COUNT_IF(is_bully) / COUNT(*), 1) AS pct_bully,
       ROUND(100.0 * COUNT_IF(outcome_type='Adoption' AND days_to_outcome>=30) / NULLIF(COUNT_IF(outcome_type='Adoption'),0), 1) AS pct_over_30d
FROM d GROUP BY 1 HAVING COUNT(*) >= 500
"""

LOOKUP = """
SELECT v.name, v.breed, v.color, g.breed_group,
       v.intake_ts::date AS came_in, v.intake_type,
       v.outcome_ts::date AS left_on, v.outcome_type,
       v.days_to_outcome AS days_waited
FROM shelter.analytics.dog_visits v
LEFT JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
WHERE UPPER(v.name) = UPPER(?)
ORDER BY v.days_to_outcome DESC NULLS LAST LIMIT 50
"""

LONGEST = """
SELECT v.name, v.breed, g.breed_group, v.days_to_outcome AS days_waited, v.outcome_type
FROM shelter.analytics.dog_visits v
LEFT JOIN shelter.analytics.breed_groups g ON v.breed = g.breed
WHERE v.days_to_outcome >= 0 AND v.name IS NOT NULL
ORDER BY v.days_to_outcome DESC LIMIT 15
"""

cuts = q(CUTS)
breeds = cuts[cuts.cut == "Breed group"].set_index("bucket").loc[ORDER].reset_index()

st.markdown(
    '<div class="hd"><div>'
    '<h1 class="claim">Black dog syndrome isn\'t real.<br>The pit bull penalty is.</h1>'
    '<p class="sub">93,965 dog visits to Austin Animal Center, 2013–2025.</p>'
    '</div>'
    '<div><span class="pill"><span class="dot"></span>Powered by Snowflake · live queries</span></div>'
    '</div>',
    unsafe_allow_html=True,
)

tiles = "".join(
    f'<div class="stat"><div class="n">{r.median_days:.0f}<small>days</small></div>'
    f'<div class="k"><span class="swatch" style="background:{c}"></span>{r.bucket}</div></div>'
    for (_, r), c in zip(breeds.iterrows(), RAMP)
)
st.markdown(f'<div class="stats">{tiles}</div>', unsafe_allow_html=True)

sec("Who waits longest", "Pick a way to slice the shelter and a thing to measure. Bars in blue are bully-type dogs or the coat colours that stand in for them.")

c1, c2, _ = st.columns([1.1, 1.1, 2])
cut = c1.selectbox("Slice by", list(dict.fromkeys(cuts.cut)), label_visibility="collapsed")
metric_label = c2.selectbox("Measure", list(METRICS), label_visibility="collapsed")
col, axis_title = METRICS[metric_label]

view = cuts[cuts.cut == cut].copy()
view["hl"] = "everything else"
if cut == "Breed group":
    view.loc[view.bucket.isin(["Pit Bull type", "Bully adjacent"]), "hl"] = "bully type"
elif cut == "Coat colour":
    view.loc[view.bucket.isin(CODED), "hl"] = "bully type"

hover = alt.selection_point(on="pointerover", fields=["bucket"], empty=True, clear="pointerout")
tips = [alt.Tooltip("bucket", title=cut), alt.Tooltip("dogs", format=","),
        alt.Tooltip("median_days", title="median days"), alt.Tooltip("pct_adopted", title="% adopted"),
        alt.Tooltip("pct_over_30d", title="% over 30d")]

base = alt.Chart(view).encode(
    x=alt.X(f"{col}:Q", title=axis_title, scale=alt.Scale(domain=[0, view[col].max() * 1.18])),
    y=alt.Y("bucket:N", title=None, sort="-x"),
)
bars = base.mark_bar(cornerRadiusEnd=4, size=26).encode(
    color=alt.Color("hl:N", title=None,
                    scale=alt.Scale(domain=["bully type", "everything else"], range=[BLUE, QUIET]),
                    legend=alt.Legend(orient="top", direction="horizontal", offset=10) if view.hl.nunique() > 1 else None),
    opacity=alt.condition(hover, alt.value(1), alt.value(0.45)),
    tooltip=tips,
).add_params(hover)
vals = base.mark_text(align="left", dx=10, fontSize=14, fontWeight=500, color="#26251f").encode(
    text=alt.Text(f"{col}:Q", format=".1f"), tooltip=tips
)
st.altair_chart(style(alt.layer(bars, vals), max(190, 44 * len(view))), use_container_width=True)
src(f"Queried live from Snowflake · {int(view.dogs.sum()):,} dogs in this slice")
with st.expander("numbers behind this chart"):
    st.dataframe(view.drop(columns=["cut", "hl"]).sort_values(col, ascending=False), hide_index=True, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

left, right = st.columns([1.25, 1])

with left:
    sec("Coat colour is standing in for breed", "One dot per colour. The further right, the more of that colour is pit bull.")
    sc = q(SCATTER)
    dots = alt.Chart(sc).mark_circle(size=260, opacity=1, stroke=SURFACE, strokeWidth=2.5).encode(
        x=alt.X("pct_bully:Q", title="share of that colour that is pit bull (%)"),
        y=alt.Y("pct_over_30d:Q", title="waited over a month (%)"),
        color=alt.value(BLUE),
        tooltip=[alt.Tooltip("primary_color", title="colour"), alt.Tooltip("pct_bully", title="% pit bull"),
                 alt.Tooltip("pct_over_30d", title="% over 30d"), alt.Tooltip("dogs", format=",")],
    )
    picked = sc[sc.primary_color.isin(["Blue", "Black", "Gray", "Cream", "Fawn"])]
    labels = alt.Chart(picked).mark_text(align="left", dx=14, fontSize=14, fontWeight=500, color="#26251f").encode(
        x="pct_bully:Q", y="pct_over_30d:Q", text="primary_color:N")
    st.altair_chart(style(alt.layer(dots, labels), 380), use_container_width=True)
    src("Queried live from Snowflake")

with right:
    sec("What the data says")
    read("<b>Black is eighth of seventeen colours.</b> Black dogs are the largest group in the shelter and are adopted more often than white dogs, 52.2% against 46.9%.")
    read("<b>Blue dogs are 81.8% pit bull.</b> It is barely a colour category — colour only predicts a long wait when it is standing in for breed.")
    read("<b>Looking the part costs 12.7 points</b> of long-stay risk, about 46% of the 27.8-point penalty carried by dogs actually labelled pit bull.")
    read("<b>One thing I can't explain:</b> pit bulls and bully-adjacent dogs are adopted at near-identical rates, 46.0% and 45.7%, yet the second group waits half as long.")

st.markdown("<hr>", unsafe_allow_html=True)

left2, right2 = st.columns([1, 1])

with left2:
    sec("Find a dog", "Every row is a real animal. Try Bella, Max, Luna, Charlie.")
    name = st.text_input("name", placeholder="Bella", label_visibility="collapsed")
    if name:
        hits = q(LOOKUP, params=(name,))
        if hits.empty:
            st.markdown('<p class="note">No dog by that name.</p>', unsafe_allow_html=True)
        else:
            st.dataframe(hits, hide_index=True, use_container_width=True, height=280)
            src(f"Queried live from Snowflake · {len(hits)} record(s) · a dog can appear more than once")

with right2:
    sec("Longest waits on record")
    st.dataframe(q(LONGEST), hide_index=True, use_container_width=True, height=340)
    src("Queried live from Snowflake")

st.markdown("<hr>", unsafe_allow_html=True)
sec("How it works",
    "Two CSVs from Austin's open data portal, 347,587 rows, loaded raw into Snowflake then typed and paired. "
    "animal_id is not unique because animals come back, so intakes and outcomes are numbered per animal and joined on visit number. "
    "Breed grouping is a rule set rather than a model, so the method is checkable line by line. "
    "Breed grouping is a rule set rather than a model, so the method is checkable line by line.")

st.markdown(
    '<div class="foot">'
    '<span><b style="color:#52514e">Powered by Snowflake</b> — 347,587 rows, every chart a live query</span>'
    '<span>Data: <a href="https://data.austintexas.gov">City of Austin open data</a>, CC0</span>'
    '<span><a href="https://github.com/thopl0/dog-adoption-analytics">SQL on GitHub</a></span>'
    '<span>Built for the DEV Weekend Challenge, August 2026</span>'
    "</div>",
    unsafe_allow_html=True,
)
