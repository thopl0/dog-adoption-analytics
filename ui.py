import altair as alt
import streamlit as st

SURFACE = "#fcfcfb"
MUTED = "#898781"
GRID = "#e6e5df"
RAMP = ["#86b6ef", "#2a78d6", "#104281"]
BLUE = "#2a78d6"
QUIET = "#cfcec6"
ACCENT = "#eb6834"

METRICS = {
    "Median days to adoption": ("median_days", "median days to adoption"),
    "Still waiting after a month": ("pct_over_30d", "% of adopted dogs that took 30+ days"),
    "Adoption rate": ("pct_adopted", "% of outcomes that were adoptions"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400&family=Inter:wght@400;500;600&display=swap');
.stApp { background: #fcfcfb; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1180px; padding-top: 1.6rem; padding-bottom: 5rem; }
html, body, [class*="css"], .stMarkdown { font-family: 'Inter', system-ui, sans-serif; }

.hd { display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; flex-wrap: wrap; margin-bottom: 0.4rem; }
h1.claim { font-family: 'Newsreader', Georgia, serif; font-weight: 400;
  font-size: clamp(1.9rem, 3.3vw, 2.6rem); line-height: 1.1; letter-spacing: -0.02em; color: #0b0b0b; margin: 0; }
p.sub { font-size: 0.89rem; color: #898781; margin: 0.5rem 0 0 0; max-width: 56ch; line-height: 1.5; }

h2.sec { font-size: 1.28rem; font-weight: 600; color: #0b0b0b; margin: 3rem 0 0.2rem 0; letter-spacing: -0.015em; }
p.note { font-size: 0.88rem; line-height: 1.55; color: #52514e; margin: 0.3rem 0 1rem 0; max-width: 88ch; }
p.read { font-size: 0.92rem; line-height: 1.6; color: #26251f; margin: 0.6rem 0 0 0; max-width: 74ch; }
p.read b { font-weight: 600; color: #0b0b0b; }
.take { font-size: 1.02rem; line-height: 1.5; color: #0b0b0b; margin: 0.3rem 0 0 0;
  border-left: 3px solid #2a78d6; padding: 0.1rem 0 0.1rem 0.85rem; max-width: 86ch; }
.take b { font-weight: 600; }

.stats { display: flex; gap: 0; border-top: 1px solid #e1e0d9; border-bottom: 1px solid #e1e0d9; margin: 1.4rem 0 0 0; }
.stat { flex: 1; padding: 0.95rem 0 1rem 0; }
.stat + .stat { border-left: 1px solid #e1e0d9; padding-left: 1.1rem; }
.stat .n { font-size: 2.05rem; font-weight: 500; line-height: 1; letter-spacing: -0.03em; color: #0b0b0b; }
.stat .n small { font-size: 0.82rem; font-weight: 400; color: #898781; margin-left: 0.25rem; letter-spacing: 0; }
.stat .k { font-size: 0.79rem; color: #52514e; margin-top: 0.38rem; }

.pill { display: inline-flex; align-items: center; gap: 0.42rem; border: 1px solid #dcdbd3; border-radius: 999px;
  padding: 0.3rem 0.7rem; font-size: 0.78rem; color: #52514e; background: #fff; white-space: nowrap; }
.pill .dot { width: 6px; height: 6px; border-radius: 999px; background: #2a78d6; }
.src { display: flex; align-items: center; gap: 0.4rem; font-size: 0.74rem; color: #a3a19a; margin: 0.3rem 0 0 0; }
.src .dot { width: 5px; height: 5px; border-radius: 999px; background: #86b6ef; flex: none; }

.refusal { font-size: 0.9rem; color: #52514e; background: #faf6f2; border: 1px solid #f0dfd2;
  border-left: 3px solid #eb6834; border-radius: 4px; padding: 0.8rem 1rem; }
.adopt { font-size: 0.9rem; line-height: 1.65; color: #26251f; background: #fff; border: 1px solid #e1e0d9;
  border-left: 3px solid #1baf7a; border-radius: 4px; padding: 0.9rem 1.15rem; margin-top: 0.7rem; }
.adopt b { font-weight: 600; }
.adopt a, .foot a, .read a { color: #2a78d6; text-decoration: none; }
.adopt a:hover, .foot a:hover { text-decoration: underline; }

.foot { display: flex; flex-wrap: wrap; gap: 0.5rem 1.4rem; align-items: center; border-top: 1px solid #e1e0d9;
  margin-top: 3rem; padding-top: 1.1rem; font-size: 0.82rem; color: #898781; }

.stTextInput input { border-radius: 6px; border: 1px solid #dcdbd3; background: #fff; font-size: 0.95rem; }
div[data-baseweb="select"] > div { border-radius: 6px; border-color: #dcdbd3; background: #fff; }
div[data-testid="stExpander"] details { border: none; border-top: 1px solid #e1e0d9; border-radius: 0; }
div[data-testid="stExpander"] summary { font-size: 0.8rem; color: #898781; }
</style>
"""

HEADER = (
    '<div class="hd"><div>'
    '<h1 class="claim">Black dog syndrome isn\'t real.<br>The pit bull penalty is.</h1>'
    '<p class="sub">Every dog Austin Animal Center has taken in since 2013, and every dog '
    'standing in it this morning.</p></div>'
    '<div style="display:flex;gap:0.45rem;flex-wrap:wrap">'
    '<span class="pill"><span class="dot"></span>Powered by Snowflake</span>'
    '<span class="pill"><span class="dot" style="background:#eb6834"></span>Powered by Google AI</span>'
    "</div></div>"
)

ADOPT = (
    '<div class="adopt">'
    "<b>These are real dogs, and you can go and get one.</b><br>"
    "Austin Animal Center · 7201 Levander Loop, Bldg A, Austin TX 78702 · "
    "walk-in adoptions daily, 11am to 7pm. Quote the animal id from the table.<br>"
    '<a href="https://www.austintexas.gov/services/adopt-pet" target="_blank">Adopt a pet</a> · '
    '<a href="https://www.austintexas.gov/animal-services" target="_blank">Austin Animal Services</a>'
    "</div>"
)

FOOTER = (
    '<div class="foot">'
    '<span><b style="color:#52514e">Powered by Snowflake</b> — every chart here is a live query</span>'
    '<span><b style="color:#52514e">Powered by Google AI</b> — Gemini reads the search box</span>'
    '<span>Data: <a href="https://data.austintexas.gov">City of Austin open data</a>, CC0</span>'
    '<span>Adopt: <a href="https://www.austintexas.gov/services/adopt-pet">Austin Animal Center</a></span>'
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
    st.markdown(f'<p class="src"><span class="dot"></span>{what}</p>', unsafe_allow_html=True)


def stats(pairs):
    tiles = "".join(f'<div class="stat"><div class="n">{n}</div><div class="k">{k}</div></div>' for n, k in pairs)
    st.markdown(f'<div class="stats">{tiles}</div>', unsafe_allow_html=True)


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


def group_colour(order, legend=None):
    return alt.Color("breed_group:N", sort=order, scale=alt.Scale(domain=order, range=RAMP), legend=legend)


def end_labels(df, x, y, order, text="breed_group:N"):
    return alt.Chart(df).mark_text(align="left", dx=12, fontSize=14, fontWeight=600).encode(
        x=x, y=y, text=text, color=group_colour(order))
