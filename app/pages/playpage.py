import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

data = pd.read_csv(ROOT/"data/processed/team_games.csv", dtype={"season": str})
data2 = pd.read_csv(ROOT/"data/processed/cases.csv", dtype={"season": str})


example = pd.DataFrame({
    "league": ["PL", "BL", "SA", "LL", "PL"],
    "season": ["2122", "2223", "2324", "2223", "2223"],
    "team": ["Man United", "Bayern Munich", "Napoli", "Sevilla", "Chelsea"],
    "sack_round": [12, 25, 12, 7, 6],
})
if "picked" not in st.session_state:
    st.session_state["picked"] = data2.sample(5).reset_index(drop=True)

picked = st.session_state["picked"]

cases = pd.DataFrame(index=example.index, columns=example.columns)
cases["league"]= picked["league"]
cases["season"]= picked["season"]
cases["team"]= picked["club"]
cases["sack_round"]= picked["decision_round"]
cases["points_swing"]= picked["points_swing"]
cases["coach"]= picked["coach"]
cases["directors_call"]= picked["directors_call"]

if "screen" not in st.session_state:
    st.session_state["screen"] = 0
    st.session_state["score"] = 0
    st.session_state["directors"] = 0
    st.session_state["rows"] = []

screen = st.session_state["screen"]

if screen == 0:
    st.title("Sack or Back", text_alignment="center")
    st.write("Five clubs in trouble. Five decisions. Would you sack the coach or back him?")

    left, middle, right = st.columns(3)

    with middle:
        if st.button("Play", type="primary", width="stretch"):
            st.session_state["screen"] = 1
            st.rerun()

elif screen <= 5:
    case = cases.iloc[screen - 1]

    league_data = data[data["league"] == case["league"]]
    season_data = league_data[league_data["season"] == case["season"]]
    team_data = season_data[season_data["team"] == case["team"]]

    before = team_data[team_data["round"] <= case["sack_round"]]
    now = before.iloc[-1]

    number_of_teams = season_data["team"].nunique()
    number_of_rounds = team_data["round"].max()

    so_far = season_data[season_data["round"] <= case["sack_round"]]
    expected_table = so_far.groupby("team")["exp_points"].sum()
    expected_ranks = expected_table.rank(ascending=False, method="min")
    expected_position = int(expected_ranks[case["team"]])

    expected_points = before["exp_points"].sum()

    last5_games = before.tail(5)
    last5_points = last5_games["points"].sum()
    last5_expected = last5_games["exp_points"].sum()

    st.progress(screen / 5)
    st.caption(f"Decision {screen} of 5")

    st.title(case["team"], text_alignment="center")
    st.subheader(f"Sack or back {case['coach']}?", text_alignment="center")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Matchday", int(now["round"]), border=True)

    with m2:
        st.metric("Position", int(now["position"]), border=True)

    with m3:
        st.metric("Expected position", expected_position, border=True)

    m4, m5 = st.columns(2)

    with m4:
        st.metric("Points", int(now["cum_points"]), delta=f"{now['cum_points'] - expected_points:+.1f} vs bookmakers", border=True)

    with m5:
        st.metric("Expected points", f"{expected_points:.1f}", border=True)

    d1, d2 = st.columns([1, 2])

    with d1:
        st.subheader("Last 5 games")
        last5 = last5_games[["opponent", "goals_for", "goals_against", "result", "points", "exp_points"]]
        last5 = last5.rename(columns={"exp_points": "expected"})
        st.dataframe(last5, hide_index=True)

    with d2:
        st.subheader("League position")
        position_chart = px.line(before, x="round", y="position", markers=True)
        position_chart.update_xaxes(range=[0.5, number_of_rounds + 0.5])
        position_chart.update_yaxes(range=[number_of_teams + 0.5, 0.5])
        position_chart.update_layout(xaxis_title="Matchday", yaxis_title="Position")
        st.plotly_chart(position_chart)

    choice = None

    b1, b2 = st.columns(2)

    with b1:
        if st.button("⬅ SACK", width="stretch"):
            choice = "Sack"

    with b2:
        if st.button("BACK ➡", width="stretch"):
            choice = "Back"

    if choice is not None:
        swing = case["points_swing"]

        if choice == "Sack":
            your_points = swing
        else:
            your_points = 0

        if case["directors_call"] == "Sack":
            director_points = swing
        else:
            director_points = 0

        st.session_state["score"] = st.session_state["score"] + your_points
        st.session_state["directors"] = st.session_state["directors"] + director_points

        st.session_state["rows"].append({
            "Club": case["team"],
            "Coach": case["coach"],
            "Matchday": int(case["sack_round"]),
            "Your call": choice,
            "Directors' call": case["directors_call"],
            "Points vs directors": round(your_points - director_points, 1),
        })
        st.session_state["screen"] = screen + 1
        st.rerun()

else:
    st.title("Full time", text_alignment="center")

    difference = st.session_state["score"] - st.session_state["directors"]

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric("Your points", f"{st.session_state['score']:+.1f}", border=True)

    with r2:
        st.metric("Directors' points", f"{st.session_state['directors']:+.1f}", border=True)

    with r3:
        st.metric("You vs directors", f"{difference:+.1f}", border=True)

    st.subheader("Your five decisions")
    results = pd.DataFrame(st.session_state["rows"])
    st.dataframe(results, hide_index=True)

    st.caption("Points = points the club won or lost over the rest of the season compared with keeping the coach. Backing the coach always counts as 0.")

    left, middle, right = st.columns(3)

    with middle:
        if st.button("Play again", type="primary", width="stretch"):
            st.session_state["screen"] = 0
            st.session_state["score"] = 0
            st.session_state["directors"] = 0
            st.session_state["rows"] = []
            st.session_state["picked"] = data2.sample(5).reset_index(drop=True)
            st.rerun()