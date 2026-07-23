"""
STREAMLIT FUNDAMENTALS — one file, every core concept.

Run with:
    pip install streamlit pandas numpy
    streamlit run streamlit_fundamentals.py

Scroll through the source top-to-bottom alongside the running app —
each section is numbered and commented so you can match code to UI.
"""

import time
import numpy as np
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────
# 1) PAGE CONFIG — must be the first Streamlit command in the script
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Streamlit Fundamentals",
    page_icon="🎈",
    layout="wide",              # "centered" or "wide"
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# 2) TEXT ELEMENTS
# ─────────────────────────────────────────────────────────────────
st.title("🎈 Streamlit Fundamentals Playground")
st.header("1. Text elements")
st.subheader("Different ways to write text")
st.write("`st.write` is the swiss-army knife — it can render text, numbers, dicts, DataFrames, charts, etc.")
st.text("st.text() — plain monospace text, no markdown parsing.")
st.markdown("**st.markdown** supports *markdown*, `code`, and even :rainbow[colors] / emoji 🎉")
st.caption("st.caption — small grey helper text, good for hints.")
st.code("print('st.code — syntax highlighted block')", language="python")
st.latex(r"e^{i\pi} + 1 = 0")
st.divider()

# ─────────────────────────────────────────────────────────────────
# 3) SIDEBAR — anything you put in st.sidebar renders in the left panel
# ─────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Sidebar controls")
name = st.sidebar.text_input("Your name", value="Learner")
age = st.sidebar.slider("Your age", 0, 100, 25)
show_balloons = st.sidebar.checkbox("Enable balloons button", value=True)
st.sidebar.info("Sidebar is great for filters/settings that shouldn't clutter the main page.")

st.header("2. Sidebar output")
st.write(f"Hello **{name}**, you are **{age}** years old. (values came from the sidebar)")

# ─────────────────────────────────────────────────────────────────
# 4) INPUT WIDGETS — the interactive core of Streamlit
# ─────────────────────────────────────────────────────────────────
st.header("3. Input widgets")

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

# ─────────────────────────────────────────────────────────────────
# 5) SESSION STATE — persist values across reruns (Streamlit reruns
#    the ENTIRE script top-to-bottom on every interaction!)
# ─────────────────────────────────────────────────────────────────
st.header("4. Session state (counter demo)")

if "counter" not in st.session_state:
    st.session_state.counter = 0  # initialize once

c1, c2, c3 = st.columns(3)
if c1.button("➖ Decrease"):
    st.session_state.counter -= 1
if c2.button("🔄 Reset"):
    st.session_state.counter = 0
if c3.button("➕ Increase"):
    st.session_state.counter += 1

st.metric(label="Counter value", value=st.session_state.counter)
st.caption("Without session_state, this counter would reset to 0 on every rerun/click.")

st.divider()

# ─────────────────────────────────────────────────────────────────
# 6) LAYOUT — columns, tabs, expander, containers
# ─────────────────────────────────────────────────────────────────
st.header("5. Layout tools")

tab1, tab2, tab3 = st.tabs(["📦 Container", "📁 Expander", "🏛️ Columns again"])

with tab1:
    container = st.container(border=True)
    container.write("This text is inside a bordered container.")
    st.write("This text is outside the container (written after, but appears where placed in code).")

with tab2:
    with st.expander("Click to expand for more details"):
        st.write("Hidden content revealed! Great for optional details, FAQs, advanced settings.")
        st.image("https://placehold.co/300x150?text=Expander+Content")

with tab3:
    left, right = st.columns([2, 1])  # unequal width ratio 2:1
    left.write("Wider column (ratio 2)")
    right.write("Narrower column (ratio 1)")

st.divider()

# ─────────────────────────────────────────────────────────────────
# 7) DATA DISPLAY — dataframes, tables, metrics, JSON
# ─────────────────────────────────────────────────────────────────
st.header("6. Displaying data")

df = pd.DataFrame(
    np.random.randn(10, 4),
    columns=["A", "B", "C", "D"]
)

st.subheader("Interactive dataframe")
st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

st.subheader("Static table")
st.table(df.head(3))

m1, m2, m3 = st.columns(3)
m1.metric("Temperature", "24°C", "1.2°C")
m2.metric("Humidity", "58%", "-3%")
m3.metric("Users", "1,204", "12")

st.subheader("Raw JSON")
st.json({"name": name, "age": age, "counter": st.session_state.counter})

st.divider()

# ─────────────────────────────────────────────────────────────────
# 8) CHARTS — built-in quick charts (no extra libraries needed)
# ─────────────────────────────────────────────────────────────────
st.header("7. Charts")

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["Series X", "Series Y", "Series Z"]
)

ct1, ct2 = st.columns(2)
with ct1:
    st.subheader("Line chart")
    st.line_chart(chart_data)
with ct2:
    st.subheader("Bar chart")
    st.bar_chart(chart_data)

st.subheader("Area chart")
st.area_chart(chart_data)

st.subheader("Map (random points)")
map_data = pd.DataFrame(
    np.random.randn(50, 2) / [50, 50] + [27.7, 85.3],  # near Kathmandu, adjust as you like
    columns=["lat", "lon"]
)
st.map(map_data)

st.divider()

# ─────────────────────────────────────────────────────────────────
# 9) STATUS ELEMENTS — feedback to the user
# ─────────────────────────────────────────────────────────────────
st.header("8. Status & feedback elements")

s1, s2, s3, s4 = st.columns(4)
s1.success("Success message")
s2.info("Info message")
s3.warning("Warning message")
s4.error("Error message")

if show_balloons and st.button("🎈 Celebrate!"):
    st.balloons()

if st.button("❄️ Snow effect"):
    st.snow()

with st.spinner("Simulating a slow task..."):
    if st.button("Run slow task"):
        time.sleep(1.5)
        st.success("Done!")

st.subheader("Progress bar demo")
if st.button("Start progress"):
    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.005)
        progress.progress(i + 1)
    st.success("Progress complete!")

st.divider()

# ─────────────────────────────────────────────────────────────────
# 10) FORMS — group inputs so the script only reruns on submit,
#     not on every single widget change (big performance win)
# ─────────────────────────────────────────────────────────────────
st.header("9. Forms (batch inputs, single rerun on submit)")

with st.form("my_form"):
    st.write("Inputs inside a form do NOT trigger a rerun until you submit.")
    f_name = st.text_input("Form: name")
    f_rating = st.slider("Form: rating", 1, 5, 3)
    submitted = st.form_submit_button("Submit form")
    if submitted:
        st.success(f"Form submitted → name={f_name!r}, rating={f_rating}")

st.divider()

# ─────────────────────────────────────────────────────────────────
# 11) CACHING — avoid re-running expensive functions on every rerun
# ─────────────────────────────────────────────────────────────────
st.header("10. Caching (st.cache_data)")

@st.cache_data
def expensive_computation(n):
    time.sleep(1)  # pretend this is slow (e.g. a DB query or big calc)
    return sum(range(n))

n_input = st.number_input("n for cached computation", value=1000, step=100)
start = time.time()
result = expensive_computation(n_input)
elapsed = time.time() - start
st.write(f"Result: {result} (took {elapsed:.3f}s — try re-running with the same n, it'll be instant!)")

st.divider()
st.caption("End of demo. Change any widget above and watch Streamlit rerun the whole script instantly. 🚀")