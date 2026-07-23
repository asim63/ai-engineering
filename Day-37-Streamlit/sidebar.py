import streamlit as st

st.sidebar.header("Sidebar controls")
name = st.sidebar.text_input("Your name", value="Learner")
age = st.sidebar.slider("Your age", 10, 100, 20)
show_balloons = st.sidebar.checkbox("Enable checkbox button", value=True)
st.sidebar.info("THis is the sidebar.")


st.header("Sidebar output")
st.write(f"Hello **{name}**, you are **{age}** years old. (values came from the sidebar)")


