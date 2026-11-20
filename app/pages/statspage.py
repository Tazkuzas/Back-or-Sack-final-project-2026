import streamlit as st
import pandas as pd
import plotly.express as px
import os

data = pd.read_csv(os.path.join(os.getcwd(), "data/processed/team_games.csv"))

leagues = data["league"].unique().tolist()
seasons = data["season"].unique().tolist()

st.title("Sacking statistics")

with st.expander("Filters"):
    f1, f2 = st.columns(2)

    with f1:
        selected_leagues = st.multiselect("League", leagues)

    with f2:
        selected_seasons = st.multiselect("Season", seasons)

m1, m2 = st.columns(2)

with m1:
    st.metric("Sackings", "–", border=True)

with m2:
    st.metric("Average matchday when sacked", "–", border=True)

m3, m4 = st.columns(2)

with m3:
    st.metric("Average position when sacked", "–", border=True)

with m4:
    st.metric("% of directors were right", "–", border=True)

c1, c2 = st.columns(2)

with c1:
    st.subheader("Sackings per matchday")
    st.info("Bar chart: x = matchday, y = sackings")

with c2:
    st.subheader("Position at sacking")
    st.info("Bar chart: x = position, y = sackings")

st.header("Was sacking the right call?")

r1, r2 = st.columns(2)

with r1:
    st.subheader("The bounce")
    st.info("Line chart: x = games before and after the sacking, y = points per game, second line = similar clubs that kept their coach")

with r2:
    st.subheader("Best and worst sackings")
    st.info("Line per sacking: position when sacked to final position, green = climbed, red = fell")

st.header("Bad or unlucky?")

u1, u2 = st.columns(2)

with u1:
    st.subheader("Luck before the sacking")
    st.info("Scatter: x = points vs expected before the sacking, y = points per game after")

with u2:
    st.metric("Sacked coaches who were only unlucky", "–", border=True)

st.header("Can a sacking be predicted?")

p1, p2 = st.columns(2)

with p1:
    st.subheader("What gets a coach sacked")
    st.info("Bar chart: one bar per factor (position, form, luck, matchday), y = effect on sacking risk")

with p2:
    st.subheader("Hot seat calculator")
    st.info("Sliders for position, form, luck and matchday, output = sacking probability")

st.divider()

st.header("Club explorer")

s1, s2, s3 = st.columns(3)

with s1:
    league = st.selectbox("League", leagues)

with s2:
    season = st.selectbox("Season", seasons)

league_data = data[data["league"] == league]
season_data = league_data[league_data["season"] == season]
clubs = season_data["team"].unique().tolist()

with s3:
    club = st.selectbox("Club", clubs)

club_data = season_data[season_data["team"] == club].copy()
club_data["luck"] = club_data["points_vs_exp"].cumsum()

number_of_teams = len(clubs)

g1, g2 = st.columns(2)

with g1:
    st.subheader("League position")
    position_chart = px.line(club_data, x="round", y="position", markers=True)
    position_chart.update_yaxes(range=[number_of_teams + 0.5, 0.5])
    position_chart.update_layout(xaxis_title="Matchday", yaxis_title="Position")
    st.plotly_chart(position_chart)

with g2:
    st.subheader("Luck")
    luck_chart = px.line(club_data, x="round", y="luck", markers=True)
    luck_chart.add_hline(y=0)
    luck_chart.update_layout(xaxis_title="Matchday", yaxis_title="Points above or below expected")
    st.plotly_chart(luck_chart)