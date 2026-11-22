import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config("Back or Sack", page_icon="⚽", layout="wide")

home_page = st.Page("pages/homepage.py", icon="🏠", title="Homepage")
data_page = st.Page("pages/statspage.py", icon="📊", title="Stats")
play_page = st.Page("pages/playpage.py", icon="▶", title= "Play")

user_pages = [home_page, play_page, data_page]

pg = st.navigation(user_pages, position="sidebar", expanded=True)

pg.run()