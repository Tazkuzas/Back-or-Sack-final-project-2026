import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent


@st.cache_data
def load_team_games():
    return pd.read_csv(ROOT / "data" / "processed" / "team_games.csv", dtype={"season": str})


data = load_team_games()

cases = pd.DataFrame({
    "league": ["PL", "BL", "SA", "LL", "PL"],
    "season": ["2122", "2223", "2324", "2223", "2223"],
    "team": ["Man United", "Bayern Munich", "Napoli", "Sevilla", "Chelsea"],
    "sack_round": [12, 25, 12, 7, 6],
})

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
    after = team_data[team_data["round"] > case["sack_round"]]
    now = before.iloc[-1]

    number_of_teams = season_data["team"].nunique()
    number_of_rounds = team_data["round"].max()

    st.progress(screen / 5)
    st.caption(f"Decision {screen} of 5")

    st.title(case["team"], text_alignment="center")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Matchday", int(now["round"]), border=True)

    with m2:
        st.metric("Position", int(now["position"]), border=True)

    with m3:
        st.metric("Points", int(now["cum_points"]), border=True)

    d1, d2 = st.columns([1, 2])

    with d1:
        st.subheader("Last 5 games")
        last5 = before[["opponent", "goals_for", "goals_against", "result"]].tail(5)
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
        ppg_before = before["points"].mean()
        ppg_after = after["points"].mean()

        if ppg_after > ppg_before:
            right_call = "Sack"
        else:
            right_call = "Back"

        if choice == right_call:
            st.session_state["score"] = st.session_state["score"] + 1

        if right_call == "Sack":
            st.session_state["directors"] = st.session_state["directors"] + 1

        st.session_state["rows"].append({
            "Club": case["team"],
            "Matchday": int(case["sack_round"]),
            "Your call": choice,
            "Points per game before": round(ppg_before, 2),
            "Points per game after": round(ppg_after, 2),
            "Right call": right_call,
        })

        st.session_state["screen"] = screen + 1
        st.rerun()

else:
    st.title("Full time", text_alignment="center")

    r1, r2 = st.columns(2)

    with r1:
        st.metric("Your score", f"{st.session_state['score']} / 5", border=True)

    with r2:
        st.metric("Real directors", f"{st.session_state['directors']} / 5", border=True)

    st.subheader("Your five decisions")
    results = pd.DataFrame(st.session_state["rows"])
    st.dataframe(results, hide_index=True)

    
    left, middle, right = st.columns(3)

    with middle:
        if st.button("Play again", type="primary", width="stretch"):
            st.session_state["screen"] = 0
            st.session_state["score"] = 0
            st.session_state["directors"] = 0
            st.session_state["rows"] = []
            st.rerun()