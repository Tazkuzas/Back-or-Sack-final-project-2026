import streamlit as st

from game import ui

ui.load_style()

if ui.home():
    st.switch_page("pages/1_Play.py")