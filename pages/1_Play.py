"""The Play page: connects logic (game/logic.py) and looks (game/ui.py).

This file only handles the game state. It decides WHICH screen to show;
logic.py computes the numbers, ui.py draws them.
"""
import streamlit as st

from game import logic, ui

CASES_PER_GAME = 5

ui.load_style()


# --- data (loaded once, then cached) ---
@st.cache_data
def get_data():
    return logic.load_data()


@st.cache_data
def get_cases():
    return logic.load_cases(get_data())


data = get_data()
cases = get_cases()


# --- game state (survives reruns) ---
def start_game():
    st.session_state["case_ids"] = logic.pick_cases(cases, CASES_PER_GAME)
    st.session_state["i"] = 0
    st.session_state["score"] = 0
    st.session_state["choice"] = None


if "case_ids" not in st.session_state:
    start_game()

i = st.session_state["i"]


# --- final screen ---
if i == CASES_PER_GAME:
    if ui.show_final(st.session_state["score"], CASES_PER_GAME):
        start_game()
        st.rerun()
    st.stop()


# --- one case ---
case_id = st.session_state["case_ids"][i]
case = logic.get_case(cases, case_id)
situation = logic.situation(data, case)
result = logic.outcome(data, case)

ui.header(i + 1, CASES_PER_GAME, st.session_state["score"])

if st.session_state["choice"] is None:
    choice = ui.swipe_card(situation, key=f"case_{case_id}")
    if choice is not None:
        st.session_state["choice"] = choice
        if choice == result["better"]:
            st.session_state["score"] += 1
        st.rerun()
else:
    if ui.show_reveal(situation, st.session_state["choice"], result):
        st.session_state["i"] += 1
        st.session_state["choice"] = None
        st.rerun()

ui.show_details(situation)