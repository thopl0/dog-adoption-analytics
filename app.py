import altair as alt
import streamlit as st

st.set_page_config(page_title="the pit bull penalty", layout="wide", initial_sidebar_state="collapsed")

import queries as Q  # noqa: E402
from ai import build_search, parse_request  # noqa: E402
from db import q  # noqa: E402
from ui import (ADOPT, COPPER, CSS, FOOTER, HEADER, INK, METRICS, QUIET, RAMP,  # noqa: E402
                SURFACE, dogcards, end_labels, group_colour, groups, numbers, read, sec, src,
                stats, style, take)

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HEADER, unsafe_allow_html=True)

ORDER = Q.BREED_GROUPS


# ── the shelter this morning ──────────────────────────────────────────────

live = q(Q.LIVE_STATS).set_index("breed_group")
roster = q(Q.ROSTER)
cuts = q(Q.CUTS)
total_now, pit_now = int(live.dogs.sum()), int(live.loc["Pit Bull type", "dogs"])

stats([
    (f"{total_now}", "dogs in the shelter this morning"),
    (f'{100 * pit_now / total_now:.0f}<small>%</small>', "of them are pit bull types"),
    ("19<small>%</small>", "of everyone who ever arrived"),
])
src("Queried live from Snowflake, and it changes every day")

take("They arrive at about the rate everything else does. They leave slower, so they pile up.")


# ── it isn't the colour ───────────────────────────────────────────────────

sec("Shelters have been warning about black dogs for years")
c1, c2 = st.columns([1.35, 1])
with c1:
    read("The idea is that black dogs get passed over, because they photograph badly or look "
         "less friendly, and so they sit in the shelter longer than everything else. Austin "
         "publishes every intake it has ever recorded, so it can be checked rather than repeated.")
    read("It doesn't hold up. Black dogs are the biggest group in the data, 24,546 of them, and "
         "they come eighth out of seventeen colours on wait time.")
    read("The colours that <b>are</b> slow are blue, fawn, and the two brindles. Those are the "
         "words people reach for when they're describing a pit bull.")
with c2:
    colours = q(Q.COLOURS)
    colours["emphasis"] = "every other colour"
    colours.loc[colours.primary_color.isin(Q.CODED_COLOURS), "emphasis"] = "the pit bull colours"
    colours.loc[colours.primary_color == "Black", "emphasis"] = "black, the one everyone blames"
    cscale = alt.Scale(domain=["the pit bull colours", "black, the one everyone blames", "every other colour"],
                       range=[COPPER, INK, QUIET])
    ctips = ["primary_color", "dogs", "pct_bully", "median_days", "pct_over_30d"]
    st.altair_chart(style(alt.Chart(colours).mark_bar(cornerRadiusEnd=3, size=13).encode(
        x=alt.X("pct_over_30d:Q", title="waited more than a month (%)"),
        y=alt.Y("primary_color:N", title=None, sort="-x"),
        color=alt.Color("emphasis:N", title=None, scale=cscale,
                        legend=alt.Legend(orient="top", direction="vertical", offset=8)),
        tooltip=ctips), 460), width='stretch')
    src()

take("<b>Blue dogs are 81.8% pit bull.</b> It was never really a question about colour.")

sc1, sc2 = st.columns([1, 1.35])
with sc2:
    dots = alt.Chart(colours).mark_circle(size=230, opacity=1, stroke=SURFACE, strokeWidth=2.5).encode(
        x=alt.X("pct_bully:Q", title="how much of that colour is pit bull (%)"),
        y=alt.Y("pct_over_30d:Q", title="waited more than a month (%)"),
        color=alt.Color("emphasis:N", title=None, scale=cscale, legend=None),
        tooltip=ctips)
    named = colours[colours.primary_color.isin(["Blue", "Black", "Gray", "Cream", "Fawn"])]
    labels = alt.Chart(named).mark_text(align="left", dx=13, fontSize=13, fontWeight=600, color=INK).encode(
        x="pct_bully:Q", y="pct_over_30d:Q", text="primary_color:N")
    st.altair_chart(style(alt.layer(dots, labels), 340), width='stretch')
    src("One dot per coat colour")
with sc1:
    read("Every dot is a coat colour. Across the bottom is how much of that colour turns out to "
         "be pit bull, and up the side is how long those dogs waited.")
    read("The two move together almost the whole way down. Black is the obvious exception, only "
         "12.4% pit bull and still slower than cream or tricolour, so colour isn't doing nothing. "
         "It just isn't doing much.")


# ── the three groups ──────────────────────────────────────────────────────

sec("So I grouped them by how much they look the part")
read("The groups come from a rule set over the 2,655 hand-typed breed strings in this data, not "
     "from a model, so you can read it and disagree with a particular line of it. The middle group "
     "is the one worth stopping on.")

bg = cuts[cuts.cut == "Breed group"].set_index("bucket")
GLOSS = {
    "Other": "everything else",
    "Bully adjacent": "boxers, cane corsos, bullmastiffs, rottweilers",
    "Pit Bull type": "called a pit bull on the paperwork",
}
groups([(g, GLOSS[g], int(bg.loc[g, "dogs"]), bg.loc[g, "median_days"], bg.loc[g, "pct_over_30d"], c)
        for g, c in zip(ORDER, RAMP)])
src("Queried live from Snowflake, 93,965 completed stays")

g1, g2 = st.columns([1.15, 1])
with g1:
    take("Nobody called the middle group pit bulls. They only look like one, and they wait "
         "<b>14 days against 8</b> for it.")
with g2:
    read("It's the same eyeballing that fills in the breed box when a dog bites somebody. There's "
         "a study on how well that works. Olson and Levy, in The Veterinary Journal, had 16 "
         "shelter staff identify 120 dogs, four of the staff being veterinarians, then ran DNA on "
         "all 120. The DNA found 25 pit bull types. The staff called 62.")


# ── thirteen years ────────────────────────────────────────────────────────

sec("And it has been this way for thirteen years")
mc, _ = st.columns([1.5, 2])
tcol, ttitle = METRICS[mc.radio("Measure", list(METRICS), horizontal=True)]

trend = q(Q.TREND)
tbase = alt.Chart(trend).encode(
    x=alt.X("yr:O", title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y(f"{tcol}:Q", title=ttitle),
    color=group_colour(ORDER),
    tooltip=["yr", "breed_group", "dogs", "median_days", "pct_over_30d", "pct_adopted"],
)
st.altair_chart(style(alt.layer(
    tbase.mark_line(strokeWidth=2.5),
    tbase.mark_circle(size=60, opacity=1, stroke=SURFACE, strokeWidth=2),
    end_labels(trend[trend.yr == trend.yr.max()], alt.X("yr:O"), alt.Y(f"{tcol}:Q"), ORDER),
).properties(padding={"right": 120}), 380), width='stretch')
src("By year of arrival. Austin changed record systems in 2025 and both eras are stitched into one "
    "timeline. The current year is excluded, its long stays haven't finished yet.")


# ── where the gap opens ───────────────────────────────────────────────────

sec("The gap opens in the first fortnight")
read("Share of each group still sitting in the shelter, day by day after they arrived.")

surv = q(Q.SURVIVAL)
sn, scv = st.columns([1, 2.2])
with scv:
    sbase = alt.Chart(surv).encode(
        x=alt.X("day:Q", title="days since arriving"),
        y=alt.Y("pct_still_there:Q", title="still not adopted (%)"),
        color=group_colour(ORDER),
        tooltip=["breed_group", "day", "pct_still_there"])
    st.altair_chart(style(alt.layer(
        sbase.mark_line(strokeWidth=2.5),
        end_labels(surv[surv.day == surv.day.max()], alt.X("day:Q"), alt.Y("pct_still_there:Q"), ORDER),
    ).properties(padding={"right": 120}), 400), width='stretch')
    src("93,965 dog visits")
with sn:
    numbers([
        ("8", "days to go home, for an ordinary dog", RAMP[0]),
        ("14", "if it only looks the part", RAMP[1]),
        ("28", "if it's called a pit bull", RAMP[2]),
    ])

take("The curves never come back together. A share of each group just never leaves, and it's much "
     "bigger for the pit bulls.")


# ── check it yourself ─────────────────────────────────────────────────────

sec("Don't take my cuts for it")
read("Slice the shelter any way you like and measure whatever you want.")

c1, c2, _ = st.columns([1.1, 1.1, 2])
cut = c1.selectbox("Slice by", list(dict.fromkeys(cuts.cut)))
mcol, maxis = METRICS[c2.selectbox("Measure", list(METRICS), index=1)]

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
    ebase.mark_bar(cornerRadiusEnd=3, size=24).encode(
        color=alt.Color("hl:N", title=None,
                        scale=alt.Scale(domain=["bully type", "everything else"], range=[COPPER, QUIET]),
                        legend=alt.Legend(orient="top", direction="horizontal", offset=10)
                        if view.hl.nunique() > 1 else None),
        opacity=alt.condition(hover, alt.value(1), alt.value(0.45)), tooltip=tips).add_params(hover),
    ebase.mark_text(align="left", dx=10, fontSize=14, fontWeight=500, color=INK).encode(
        text=alt.Text(f"{mcol}:Q", format=".1f"), tooltip=tips),
), max(190, 44 * len(view))), width='stretch')
src(f"{int(view.dogs.sum()):,} dogs in this slice")


# ── find one ──────────────────────────────────────────────────────────────

sec("So go and find one")
read("Ask in plain English. Gemini turns your sentence into a filter, Snowflake runs it against "
     "the dogs actually in the building. It only answers questions about these dogs, so try it "
     "with something else.")

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
        st.dataframe(hits, hide_index=True, width='stretch', height=300)
        src(f"{model} read the request, then Snowflake returned {len(hits)} dogs")
        st.markdown(ADOPT, unsafe_allow_html=True)
        with st.expander("what Gemini actually sent to Snowflake, and note it never writes SQL"):
            st.json(filters)
            st.code(sql.strip() + "\n-- bound params: " + repr(params), language="sql")


# ── the ones who have waited longest ──────────────────────────────────────

longest = roster.head(8)
n_longest = len(longest)
pit_longest = int((longest.breed_group == "Pit Bull type").sum())
top_is_pit = bool(len(longest)) and longest.iloc[0].breed_group == "Pit Bull type"

sec("These eight are still waiting, this morning")
read("Everything above is an argument about a category. These are animals in a building in Texas, "
     "and every one of them was still there when this page loaded.")

dogcards(longest, tint=dict(zip(ORDER, RAMP)))
src("The longest waits in the shelter right now, coloured by group")

take(f"<b>{pit_longest} of the {n_longest}</b> longest waits in the building are pit bull types. "
     + ("The longest of all is one too. " if top_is_pit else "The longest of all isn't. ")
     + "It's the roster, sorted.")

f1, f2 = st.columns(2)
groups_pick = f1.multiselect("Breed group", ORDER, default=ORDER)
min_days = f2.slider("Waiting at least (days)", 0, int(roster.days_waiting.max()), 0)
shown = roster[roster.breed_group.isin(groups_pick) & (roster.days_waiting >= min_days)]
st.dataframe(shown, hide_index=True, width='stretch', height=340)
src(f"{len(shown)} of {len(roster)} dogs, of which "
    f"{100 * (shown.breed_group == 'Pit Bull type').mean() if len(shown) else 0:.0f}% are pit bull types")
st.markdown(ADOPT, unsafe_allow_html=True)


# ── method ────────────────────────────────────────────────────────────────

rep = q(Q.REPEATS).iloc[0]
sec("How this was built, and where it could be wrong")

m1, m2 = st.columns([1.25, 1])
with m1:
    read("Four feeds from Austin's open data portal, about 380,000 rows, land raw in Snowflake as "
         "text and get typed on the way out. Austin replaced its record system in May 2025, so the "
         "two eras use different schemas and incompatible animal ids. They're analysed separately "
         "and only ever stitched together at the chart level.")
    read(f"Pairing arrivals to departures is the awkward part. <code>animal_id</code> isn't unique, "
         f"because <b>{rep.pct_repeat}%</b> of visits are a dog coming back and one animal returned "
         f"{int(rep.most_visits)} times. Joining on the id alone multiplies those into records that "
         f"never happened, so each side gets numbered per animal and joined on visit number.")
    read("<b>The one that cuts at me:</b> Austin's breed column is shelter staff writing down what "
         "they think a dog is, which is the same instrument this whole page is about. My pit bull "
         "group is dogs that people called pit bulls. I wasn't measuring genetics, I was measuring "
         "what happens to a dog that gets seen a certain way.")
    read("None of this says anything about whether pit bulls are dangerous. I went looking for "
         "that, decided the data couldn't answer it honestly, and stopped.")
    read("Rottweilers are in the middle group on how people read them, not on taxonomy. That's a "
         "judgement call and it's mine. Gemini never writes SQL, it turns a sentence into JSON and "
         "Python whitelists every field before anything runs.")
with m2:
    read("<b>Everything got slower, so is this just the new system counting differently?</b>")
    era = q(Q.ERA_CHECK).pivot(index="outcome_type", columns="era", values="median_days")
    st.dataframe(era.reindex(["Adoption", "Transfer", "Return to Owner"]), width='stretch')
    read("If it were, every outcome would have shifted. Transfers take the same five days they "
         "always did. Adoption went from 9 days to 28, and adoption is the one that needs a member "
         "of the public to pick a dog.")
    read("<b>What I can't explain:</b> pit bulls and bully adjacent dogs get adopted at almost the "
         "same rate, 46.0% and 45.7%, but the second group waits half as long. I'm reporting it "
         "rather than explaining it away.")

st.markdown(FOOTER, unsafe_allow_html=True)
