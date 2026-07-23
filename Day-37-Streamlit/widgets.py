import streamlit as st 
st.header("Input widgets")

col1, col2, col3 = st.columns(3)  # LAYOUT: split into 3 equal columns

with col1:
    st.subheader("Buttons & toggles")
    clicked = st.button("Click me")
    toggled = st.toggle("Toggle me")
    checked = st.checkbox("Check me")
    if clicked:
        st.success("Button was clicked!")
    if toggled:
        st.info("Toggle is ON")
    if checked:
        st.warning("Checkbox is checked")

with col2:
    st.subheader("Selectors")
    choice = st.radio("Pick one", ["Option A", "Option B", "Option C"])
    dropdown = st.selectbox("Choose a fruit", ["Apple", "Banana", "Cherry"])
    multi = st.multiselect("Pick several", ["Python", "JS", "Rust", "Go"], default=["Python"])
    st.write("Radio:", choice, "| Selectbox:", dropdown, "| Multiselect:", multi)

with col3:
    st.subheader("Numeric & text")
    number = st.number_input("Pick a number", min_value=0, max_value=10, value=5)
    slider_val = st.slider("Pick a range", 0, 100, (20, 80))
    text = st.text_input("Type something", placeholder="e.g. hello")
    area = st.text_area("Multi-line text", placeholder="type more here...")
    st.write("Number:", number, "| Range:", slider_val)

st.subheader("Date, time & file upload")
d = st.date_input("Pick a date")
t = st.time_input("Pick a time")
uploaded = st.file_uploader("Upload a file (optional)", type=["csv", "txt"])
color = st.color_picker("Pick a color", "#00f900")
st.write(f"Date: {d} | Time: {t} | Color: {color}")
if uploaded is not None:
    st.success(f"Uploaded: {uploaded.name}")

st.divider()