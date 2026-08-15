import altair as alt
import streamlit as st

st.set_page_config(page_title="the pit bull penalty", layout="wide", initial_sidebar_state="collapsed")

import queries as Q  # noqa: E402
from ai import build_search, parse_request  # noqa: E402
from db import q  # noqa: E402
from ui import (ACCENT, ADOPT, BLUE, CSS, FOOTER, HEADER, METRICS, QUIET, RAMP,  # noqa: E402
                SURFACE, end_labels, group_colour, read, sec, src, stats, style, take)

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HEADER, unsafe_allow_html=True)

ORDER = Q.BREED_GROUPS


# ── the finding ───────────────────────────────────────────────────────────

trend = q(Q.TREND)
tcol, ttitle = METRICS[st.radio("m", list(METRICS), horizontal=True, label_visibility="collapsed")]

tbase = alt.Chart(trend).encode(
    x=alt.X("yr:O", title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y(f"{tcol}:Q", title=ttitle),
    color=group_colour(ORDER),
    tooltip=["yr", "breed_group", "dogs", "median_days", "pct_over_30d", "pct_adopted"],
)
st.altair_chart(style(alt.layer(
    tbase.mark_line(strokeWidth=3),
    tbase.mark_circle(size=70, opacity=1, stroke=SURFACE, strokeWidth=2),
    end_labels(trend[trend.yr == trend.yr.max()], alt.X("yr:O"), alt.Y(f"{tcol}:Q"), ORDER),
).properties(padding={"right": 120}), 400), use_container_width=True)
src("Queried live from Snowflake · by year of arrival · Austin changed record systems in 2025 and both "
    "are stitched into one timeline · the current year is excluded, its long stays haven't finished")

take("Three groups of dog, one shelter, thirteen years. <b>They do not wait the same amount of time, "
     "and they never have.</b>")


# ── it isn't the colour ───────────────────────────────────────────────────

sec("It isn't the coat colour, though that's what everyone blames",
    "Shelters have warned for years that black dogs get overlooked. Austin publishes every intake, so it "
    "can simply be checked — here is wait time by coat colour, and how much of each colour is pit bull.")

colours = q(Q.COLOURS)
colours["emphasis"] = "every other colour"
colours.loc[colours.primary_color.isin(Q.CODED_COLOURS), "emphasis"] = "the pit bull colours"
colours.loc[colours.primary_color == "Black", "emphasis"] = "black, the one everyone blames"
cscale = alt.Scale(domain=["the pit bull colours", "black, the one everyone blames", "every other colour"],
                   range=[BLUE, ACCENT, QUIET])
ctips = ["primary_color", "dogs", "pct_bully", "median_days", "pct_over_30d"]

left, right = st.columns(2)
with left:
    st.altair_chart(style(alt.Chart(colours).mark_bar(cornerRadiusEnd=3, size=15).encode(
        x=alt.X("pct_over_30d:Q", title="waited more than a month (%)"),
        y=alt.Y("primary_color:N", title=None, sort="-x"),
        color=alt.Color("emphasis:N", title=None, scale=cscale,
                        legend=alt.Legend(orient="top", direction="vertical", offset=10)),
        tooltip=ctips), 470), use_container_width=True)
    src()
with right:
    dots = alt.Chart(colours).mark_circle(size=250, opacity=1, stroke=SURFACE, strokeWidth=2.5).encode(
        x=alt.X("pct_bully:Q", title="how much of that colour is pit bull (%)"),
        y=alt.Y("pct_over_30d:Q", title="waited more than a month (%)"),
        color=alt.Color("emphasis:N", title=None, scale=cscale, legend=None),
        tooltip=ctips)
    named = colours[colours.primary_color.isin(["Blue", "Black", "Gray", "Cream", "Fawn"])]
    labels = alt.Chart(named).mark_text(align="left", dx=13, fontSize=13, fontWeight=600, color="#26251f").encode(
        x="pct_bully:Q", y="pct_over_30d:Q", text="primary_color:N")
    st.altair_chart(style(alt.layer(dots, labels), 470), use_container_width=True)
    src("Queried live from Snowflake · one dot per coat colour")

take("Black sits eighth of seventeen, and is adopted more often than white. The four slowest colours — "
     "blue, fawn, and the two brindles — are the words people use to describe a pit bull. "
     "<b>Blue dogs are 81.8% pit bull. It is barely a colour at all.</b>")


# ── where the gap opens ───────────────────────────────────────────────────

sec("The gap opens in the first fortnight and never closes",
    "Share of each group still sitting in the shelter, day by day after arrival.")

surv = q(Q.SURVIVAL)
sbase = alt.Chart(surv).encode(
    x=alt.X("day:Q", title="days since arriving"),
    y=alt.Y("pct_still_there:Q", title="still not adopted (%)"),
    color=group_colour(ORDER),
    tooltip=["breed_group", "day", "pct_still_there"])
st.altair_chart(style(alt.layer(
    sbase.mark_line(strokeWidth=3),
    end_labels(surv[surv.day == surv.day.max()], alt.X("day:Q"), alt.Y("pct_still_there:Q"), ORDER),
).properties(padding={"right": 120}), 360), use_container_width=True)
src("Queried live from Snowflake · 93,965 dog visits")

take("An ordinary dog goes home in <b>8 days</b>. One that merely looks like a pit bull takes <b>14</b>. "
     "An actual pit bull takes <b>28</b>. The curves never reconverge — it isn't that pit bulls catch up "
     "slowly, it's that a fixed share of them never leave at all.")


# ── check it yourself ─────────────────────────────────────────────────────

sec("Don't take my cuts for it", "Slice the shelter any way you like, measure whatever you want.")

cuts = q(Q.CUTS)
c1, c2, _ = st.columns([1.1, 1.1, 2])
cut = c1.selectbox("Slice by", list(dict.fromkeys(cuts.cut)), label_visibility="collapsed")
mcol, maxis = METRICS[c2.selectbox("Measure", list(METRICS), index=1, label_visibility="collapsed")]

view = cuts[cuts.cut == cut].copy()
view["hl"] = "everything else"
if cut == "Breed group":
    view.loc[view.bucket.isin(["Pit Bull type", "Bully adjacent"]), "hl"] = "bully type"
elif cut == "Coat colour":
    view.loc[view.bucket.isin(Q.CODED_COLOURS), "hl"] = "bully type"

hover = alt.selection_point(on="pointerover", fields=["bucket"], empty=True, clear="pointerout")
tips = [alt.Tooltip("bucket", title=cut), alt.Tooltip("dogs", format=","),
        alt.Tooltip("median_days", title="median days"), alt.Tooltip("pct_adopted", title="% adopted"),
        alt.Tooltip("pct_over_30d", title="% over 30d")]
ebase = alt.Chart(view).encode(
    x=alt.X(f"{mcol}:Q", title=maxis, scale=alt.Scale(domain=[0, view[mcol].max() * 1.18])),
    y=alt.Y("bucket:N", title=None, sort="-x"))
st.altair_chart(style(alt.layer(
    ebase.mark_bar(cornerRadiusEnd=4, size=26).encode(
        color=alt.Color("hl:N", title=None,
                        scale=alt.Scale(domain=["bully type", "everything else"], range=[BLUE, QUIET]),
                        legend=alt.Legend(orient="top", direction="horizontal", offset=10)
                        if view.hl.nunique() > 1 else None),
        opacity=alt.condition(hover, alt.value(1), alt.value(0.45)), tooltip=tips).add_params(hover),
    ebase.mark_text(align="left", dx=10, fontSize=14, fontWeight=500, color="#26251f").encode(
        text=alt.Text(f"{mcol}:Q", format=".1f"), tooltip=tips),
), max(190, 44 * len(view))), use_container_width=True)
src(f"Queried live from Snowflake · {int(view.dogs.sum()):,} dogs in this slice")


# ── right now ─────────────────────────────────────────────────────────────

live = q(Q.LIVE_STATS).set_index("breed_group")
roster = q(Q.ROSTER)
total_now, pit_now = int(live.dogs.sum()), int(live.loc["Pit Bull type", "dogs"])

sec("Which is why the shelter looks like this today",
    "Pit bulls arrive at roughly the rate everything else does. They leave slower, so they pile up.")
stats([
    (f"{total_now}", "dogs in the shelter this morning"),
    (f'{100 * pit_now / total_now:.0f}<small>%</small>', "of them are pit bull types"),
    ("19<small>%</small>", "of everyone who ever arrived"),
    (f'{live.loc["Pit Bull type", "avg_days_waiting"]:.0f}'
     f'<small>vs {live.loc["Other", "avg_days_waiting"]:.0f} days</small>', "waiting so far, pit bull vs other"),
])
src()
take("<b>One in five dogs coming through the door. Two in five of the dogs standing in it.</b> "
     "The penalty isn't abstract — it's what the shelter is full of.")


# ── find one ──────────────────────────────────────────────────────────────

sec("So go and find one",
    "Ask in plain English. Gemini turns your sentence into a filter, Snowflake runs it against the dogs "
    "actually in the building. It only answers questions about these dogs — try it with something else.")

box, _ = st.columns([1.4, 1])
question = box.text_input("ask", placeholder="a young pit bull who's been waiting more than three months",
                          label_visibility="collapsed")
if st.button("Search", type="primary") and question:
    try:
        st.session_state["filters"] = parse_request(question)
    except Exception as e:
        st.session_state["filters"] = ({"relevant": False, "refusal": f"Gemini is unavailable ({e})."}, None)

filters, model = st.session_state.get("filters", (None, None))
if filters and not filters.get("relevant"):
    st.markdown(f'<p class="refusal">{filters.get("refusal") or "That is not something this can answer."}</p>',
                unsafe_allow_html=True)
    src(f"Rejected by {model} before any query ran")
elif filters:
    sql, params = build_search(filters)
    hits = q(sql, params=tuple(params))
    read(f'<b>{filters.get("summary", "")}</b>')
    if hits.empty:
        st.markdown('<p class="note">No dogs match that. Try loosening it.</p>', unsafe_allow_html=True)
    else:
        st.dataframe(hits, hide_index=True, use_container_width=True, height=300)
        src(f"{model} read the request · Snowflake returned {len(hits)} dogs")
        st.markdown(ADOPT, unsafe_allow_html=True)
        with st.expander("what Gemini actually sent to Snowflake — it never writes SQL"):
            st.json(filters)
            st.code(sql.strip() + "\n-- bound params: " + repr(params), language="sql")

sec("Or read the whole kennel", "All of them, longest wait first.")
f1, f2 = st.columns(2)
groups = f1.multiselect("breed group", ORDER, default=ORDER, label_visibility="collapsed")
min_days = f2.slider("waiting at least (days)", 0, int(roster.days_waiting.max()), 0, label_visibility="collapsed")
shown = roster[roster.breed_group.isin(groups) & (roster.days_waiting >= min_days)]
st.dataframe(shown, hide_index=True, use_container_width=True, height=340)
src(f"Queried live from Snowflake · {len(shown)} of {len(roster)} dogs · "
    f"{100 * (shown.breed_group == 'Pit Bull type').mean() if len(shown) else 0:.0f}% pit bull type here")
st.markdown(ADOPT, unsafe_allow_html=True)


# ── method ────────────────────────────────────────────────────────────────

rep = q(Q.REPEATS).iloc[0]
sec("How this was built, and where it could be wrong")

m1, m2 = st.columns([1.25, 1])
with m1:
    read("Four feeds from Austin's open data portal, about 380,000 rows, land raw in Snowflake as text "
         "and are typed on the way out. Austin replaced its record system in May 2025, so the two eras "
         "use different schemas and incompatible animal ids — they are analysed separately and only ever "
         "stitched at the chart level, never merged in the warehouse.")
    read(f"Pairing arrivals to departures is the awkward part. <code>animal_id</code> is not unique because "
         f"<b>{rep.pct_repeat}%</b> of visits are a dog coming back — one animal returned {int(rep.most_visits)} "
         f"times. Joining on the id alone multiplies those into records that never happened, so each side is "
         f"numbered per animal and joined on visit number.")
    read("Breed grouping is a SQL rule set, not a model. This is an argument about bias, so the method "
         "should be checkable line by line rather than trusted. It lives in a Snowflake function so the "
         "historical and live sides cannot drift apart. Rottweilers are in the middle group on how people "
         "read them, not on taxonomy — that is a judgement call, and it is mine.")
    read("Gemini never writes SQL. It turns a sentence into JSON, Python whitelists every field against "
         "known values, and free text goes in as a bound parameter.")
with m2:
    read("<b>Everything got slower, so is this just the new system counting differently?</b>")
    era = q(Q.ERA_CHECK).pivot(index="outcome_type", columns="era", values="median_days")
    st.dataframe(era.reindex(["Adoption", "Transfer", "Return to Owner"]), use_container_width=True)
    read("No. If it were, every outcome would have shifted. Transfers take the same five days they always "
         "did. Only adoption moved — the one outcome that needs a member of the public to choose a dog.")
    read("<b>What I can't explain:</b> pit bulls and bully-adjacent dogs are adopted at almost identical "
         "rates, 46.0% and 45.7%, yet the second group waits half as long. Two penalties that don't move "
         "together. I'm reporting it rather than explaining it away.")

st.markdown(FOOTER, unsafe_allow_html=True)
