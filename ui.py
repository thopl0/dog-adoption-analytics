import altair as alt
import streamlit as st

SURFACE = "#fbf9f5"
MUTED = "#8a857c"
GRID = "#e8e3d9"
RAMP = ["#dd9455", "#bf5f28", "#782d12"]
COPPER = "#bf5f28"
INK = "#2b2926"
QUIET = "#d5d0c6"

METRICS = {
    "Median days to adoption": ("median_days", "median days to adoption"),
    "Still waiting after a month": ("pct_over_30d", "% of adopted dogs that took 30+ days"),
    "Adoption rate": ("pct_adopted", "% of outcomes that were adoptions"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;500&family=Geist:wght@400;500;600&display=swap');
.stApp { background: #fbf9f5; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1180px; padding-top: 2.4rem; padding-bottom: 6rem; }
html, body, [class*="css"], .stMarkdown { font-family: 'Geist', system-ui, sans-serif; }

.hd { max-width: 900px; margin-bottom: 3rem; }
h1.claim { font-family: 'Newsreader', Georgia, serif; font-weight: 400;
  font-size: clamp(2.1rem, 3.9vw, 3rem); line-height: 1.14; letter-spacing: -0.018em;
  color: #17150f; margin: 0; }
p.sub { font-size: 1.16rem; color: #57534b; margin: 1.4rem 0 0 0; max-width: 60ch; line-height: 1.62; }
.pills { display: flex; gap: 0.55rem; flex-wrap: wrap; margin-top: 1.8rem; }

h2.sec { font-family: 'Newsreader', Georgia, serif; font-weight: 400; font-size: 2.05rem; color: #17150f;
  margin: 5.5rem 0 0 0; letter-spacing: -0.015em; line-height: 1.24; max-width: 24ch; }
p.note { font-size: 1.06rem; line-height: 1.7; color: #57534b; margin: 1rem 0 1.7rem 0; max-width: 58ch; }
p.read { font-size: 1.06rem; line-height: 1.75; color: #2b2926; margin: 1.05rem 0 0 0; max-width: 58ch; }
p.read b { font-weight: 600; color: #17150f; }
.take { font-family: 'Newsreader', Georgia, serif; font-size: 1.62rem; line-height: 1.45; color: #17150f;
  margin: 2.8rem 0 1.6rem 0; padding: 0.15rem 0 0.15rem 1.4rem; border-left: 2px solid #bf5f28; max-width: 46ch; }
.take b { font-weight: 500; color: #782d12; }

.stats { display: flex; flex-wrap: nowrap; gap: 3.4rem; margin: 0 0 0.4rem 0; }
.stat { flex: 0 1 auto; }
.stat .n { font-family: 'Newsreader', Georgia, serif; font-size: 3.5rem; font-weight: 400; line-height: 1;
  letter-spacing: -0.02em; color: #17150f; }
.stat .n small { font-family: 'Geist', sans-serif; font-size: 1.05rem; font-weight: 400; color: #8a857c;
  margin-left: 0.3rem; letter-spacing: 0; }
.stat .k { font-size: 1rem; color: #57534b; margin-top: 0.7rem; max-width: 34ch; line-height: 1.5;
  white-space: nowrap; }

.nums { display: flex; flex-direction: column; gap: 2.2rem; margin-top: 2.6rem; }
.num { border-left: 2px solid; padding-left: 1.2rem; }
.num b { display: block; font-family: 'Newsreader', Georgia, serif; font-size: 3.3rem; font-weight: 400;
  line-height: 1; letter-spacing: -0.02em; color: #17150f; }
.num span { display: block; font-size: 1rem; color: #57534b; margin-top: 0.55rem; line-height: 1.5; max-width: 26ch; }

.grp { margin: 0; }
.grp .row { display: grid; grid-template-columns: 1.8fr repeat(3, 1fr); gap: 1rem; align-items: baseline;
  padding: 1.15rem 0 1.2rem 1.1rem; border-top: 1px solid #e8e3d9; border-left: 2px solid transparent; }
.grp .row:last-child { border-bottom: 1px solid #e8e3d9; }
.grp .row.hd2 { padding: 0 0 0.55rem 1.1rem; border-top: none; }
.grp .row.hd2 span { font-size: 0.92rem; color: #8a857c; }
.grp .nm { font-size: 1.14rem; font-weight: 500; color: #17150f; }
.grp .nm em { display: block; font-style: normal; font-size: 0.95rem; font-weight: 400; color: #8a857c;
  margin-top: 0.3rem; line-height: 1.5; }
.grp .v { font-family: 'Newsreader', Georgia, serif; font-size: 2.4rem; font-weight: 400;
  letter-spacing: -0.02em; color: #17150f; }
.grp .v small { font-family: 'Geist', sans-serif; font-size: 0.95rem; color: #8a857c; margin-left: 0.1rem; }
@media (max-width: 700px) { .grp .row { grid-template-columns: 1fr 1fr; row-gap: 0.6rem; } }

.dogs { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0 2rem; margin: 0; }
.dog { border-top: 2px solid #bf5f28; padding: 1rem 0 1.6rem 0; }
.dog .d { font-family: 'Newsreader', Georgia, serif; font-size: 2.7rem; font-weight: 400; line-height: 1;
  letter-spacing: -0.02em; color: #17150f; }
.dog .d small { font-family: 'Geist', sans-serif; font-size: 0.92rem; color: #8a857c; margin-left: 0.35rem; }
.dog .nm { font-size: 1.12rem; font-weight: 500; color: #17150f; margin-top: 0.75rem; }
.dog .mt { font-size: 0.95rem; color: #8a857c; margin-top: 0.28rem; line-height: 1.55; }
@media (max-width: 900px) { .dogs { grid-template-columns: repeat(2, 1fr); gap: 0 1.4rem; } }

.pill { display: inline-flex; align-items: center; gap: 0.45rem; border: 1px solid #e2ddd2; border-radius: 999px;
  padding: 0.4rem 0.9rem; font-size: 0.95rem; color: #57534b; background: #fffefc; white-space: nowrap; }
.pill .dot { width: 7px; height: 7px; border-radius: 999px; background: #bf5f28; }
.src { font-size: 0.92rem; color: #a49e93; margin: 0.9rem 0 0.6rem 0; line-height: 1.55; max-width: 62ch; }

.refusal { font-size: 1.04rem; color: #57534b; background: #f6f3ec; border: 1px solid #e2ddd2;
  border-left: 3px solid #a49e93; border-radius: 4px; padding: 1rem 1.2rem; }
.adopt { font-size: 1.02rem; line-height: 1.7; color: #2b2926; background: #fffefc; border: 1px solid #e8e3d9;
  border-left: 3px solid #4a7c59; border-radius: 4px; padding: 1.1rem 1.3rem; margin-top: 1rem; }
.adopt b { font-weight: 600; }
.adopt a, .foot a, .read a { color: #bf5f28; text-decoration: none; }
.adopt a:hover, .foot a:hover { text-decoration: underline; }

.foot { display: flex; flex-wrap: wrap; gap: 0.6rem 1.8rem; align-items: center; border-top: 1px solid #e8e3d9;
  margin-top: 4rem; padding-top: 1.4rem; font-size: 0.95rem; color: #8a857c; }

.stTextInput input { border-radius: 6px; border: 1px solid #e2ddd2; background: #fffefc; font-size: 1.05rem;
  padding: 0.7rem 0.9rem; }
div[data-baseweb="select"] > div { border-radius: 6px; border-color: #e2ddd2; background: #fffefc; font-size: 1rem; }
div[data-testid="stExpander"] details { border: none; border-top: 1px solid #e8e3d9; border-radius: 0; }
div[data-testid="stExpander"] summary { font-size: 0.95rem; color: #8a857c; }
label[data-testid="stWidgetLabel"] p { font-size: 0.95rem; color: #57534b; font-weight: 500; }
div[role="radiogroup"] label p { font-size: 1rem; }
.stSlider label, .stMultiSelect label { font-size: 0.95rem; }
</style>
"""

HEADER = (
    '<div class="hd">'
    '<h1 class="claim">A dog that only looks like a pit bull<br>waits nearly twice as long.</h1>'
    '<p class="sub">Nobody wrote pit bull on its paperwork. Every dog Austin Animal Center has '
    'taken in since 2013, and every dog standing in it this morning.</p>'
    '<div class="pills">'
    '<span class="pill"><span class="dot"></span>Powered by Snowflake</span>'
    '<span class="pill"><span class="dot"></span>Powered by Google AI</span>'
    "</div></div>"
)

ADOPT = (
    '<div class="adopt">'
    "<b>These are real dogs, and you can go and get one.</b><br>"
    "Austin Animal Center, 7201 Levander Loop Bldg A. Walk-in adoptions daily, 11am to 7pm. "
    "Quote the animal id from the table.<br>"
    '<a href="https://www.austintexas.gov/services/adopt-pet" target="_blank">Adopt a pet</a> · '
    '<a href="https://www.austintexas.gov/animal-services" target="_blank">Austin Animal Services</a>'
    "</div>"
)

FOOTER = (
    '<div class="foot">'
    '<span><b style="color:#57534b">Powered by Snowflake</b>, every chart here is a live query</span>'
    '<span><b style="color:#57534b">Powered by Google AI</b>, Gemini reads the search box</span>'
    '<span>Data: <a href="https://data.austintexas.gov">City of Austin open data</a>, CC0</span>'
    '<span><a href="https://github.com/thopl0/dog-adoption-analytics">SQL and app on GitHub</a></span>'
    "<span>DEV Weekend Challenge, August 2026</span></div>"
)


def sec(title, note=None):
    st.markdown(f'<h2 class="sec">{title}</h2>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<p class="note">{note}</p>', unsafe_allow_html=True)


def take(text):
    st.markdown(f'<p class="take">{text}</p>', unsafe_allow_html=True)


def read(text):
    st.markdown(f'<p class="read">{text}</p>', unsafe_allow_html=True)


def src(what="Queried live from Snowflake"):
    st.markdown(f'<p class="src">{what}</p>', unsafe_allow_html=True)


def stats(pairs):
    tiles = "".join(f'<div class="stat"><div class="n">{n}</div><div class="k">{k}</div></div>' for n, k in pairs)
    st.markdown(f'<div class="stats">{tiles}</div>', unsafe_allow_html=True)


def groups(rows):
    # rows are (name, gloss, dogs, median_days, pct_over_30d, colour)
    head = ('<div class="row hd2"><span>breed group</span><span>dogs</span>'
            '<span>median days</span><span>waited over a month</span></div>')
    body = "".join(
        f'<div class="row" style="border-left-color:{c}">'
        f'<div class="nm">{n}<em>{gloss}</em></div>'
        f'<div class="v">{dogs:,}</div>'
        f'<div class="v">{days:.0f}</div>'
        f'<div class="v">{over:.1f}<small>%</small></div></div>'
        for n, gloss, dogs, days, over, c in rows)
    st.markdown(f'<div class="grp">{head}{body}</div>', unsafe_allow_html=True)


def numbers(rows):
    # rows are (value, caption, colour) — colour ties each number to its line on the chart beside it
    items = "".join(f'<div class="num"><b style="color:{c}">{v}</b><span>{k}</span></div>' for v, k, c in rows)
    st.markdown(f'<div class="nums">{items}</div>', unsafe_allow_html=True)


def _txt(v, fallback):
    # nulls arrive as None or NaN depending on the column, and NaN is truthy, so `or` isn't enough
    return fallback if v is None or v != v or not str(v).strip() else str(v).strip()


def dogcards(df, n=8, tint=None):
    cards = []
    for _, d in df.head(n).iterrows():
        days = d.get("days_waiting")
        if days is None or days != days:
            continue
        age = d.get("age_years")
        age = f"{int(age)} years old" if age is not None and age == age else "age not on file"
        rule = (tint or {}).get(d.get("breed_group"), COPPER)
        cards.append(
            f'<div class="dog" style="border-top-color:{rule}">'
            f'<div class="d">{int(days)}<small>days so far</small></div>'
            f'<div class="nm">{_txt(d.get("name"), "No name on file")}</div>'
            f'<div class="mt">{_txt(d.get("breed"), "Breed not recorded")}<br>{age}</div></div>'
        )
    st.markdown(f'<div class="dogs">{"".join(cards)}</div>', unsafe_allow_html=True)


def style(chart, height):
    return (
        chart.properties(height=height, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True, gridColor=GRID, gridWidth=1, domain=False, tickSize=0,
                        labelColor="#57534b", titleColor=MUTED, labelFontSize=15, titleFontSize=14,
                        labelPadding=10, titlePadding=18, labelFont="Geist", titleFont="Geist")
        .configure_legend(labelColor="#57534b", labelFont="Geist", labelFontSize=15,
                          symbolType="square", symbolSize=170)
        .configure_text(font="Geist")
    )


def group_colour(order, legend=None):
    return alt.Color("breed_group:N", sort=order, scale=alt.Scale(domain=order, range=RAMP), legend=legend)


def end_labels(df, x, y, order, text="breed_group:N"):
    return alt.Chart(df).mark_text(align="left", dx=12, fontSize=14, fontWeight=600).encode(
        x=x, y=y, text=text, color=group_colour(order))
