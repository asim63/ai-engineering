import streamlit as st 

st.header("Session state")

if "counter" not in st.session_state:
    st.session_state.counter = 0  # initialize once

c1, c2, c3 = st.columns(3)
if c1.button("Decrease"):
    st.session_state.counter -= 1
if c2.button("Reset"):
    st.session_state.counter = 0
if c3.button("Increase"):
    st.session_state.counter += 1

st.metric(label="Counter value", value=st.session_state.counter)
st.caption("Without session_state, this counter would reset to 0 on every rerun/click.")

st.divider()