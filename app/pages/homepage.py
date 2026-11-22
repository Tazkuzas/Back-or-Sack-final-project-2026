import streamlit as st

st.title("Back or Sack", text_alignment="center")

col1, col2, col3 = st.columns(3, border=True)

with col1:
    st.caption("01")
    st.subheader("READ THE ROOM", text_alignment="center")


with col2:
    st.caption("02")
    st.subheader("SWIPE", text_alignment="center")


with col3:
    st.caption("03")
    st.subheader("FACE THE DATA", text_alignment="center")



if st.button("Play", type="primary", width="stretch"):
    st.switch_page("pages/playpage.py")


st.divider()

st.subheader("Questions we try to answer:")

q1 = st.container(border=True)

with q1:
    st.write("Was sacking the coach a right call?")

q2 = st.container(border=True)

with q2:
    st.write("Was the coach actually bad or simply unlucky?")

q3 = st.container(border=True)

with q3:
    st.write("Can you beat the real sporting directors?")