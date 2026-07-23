import streamlit as st


st.title("Streamlit Fundamentals Playground")
st.header("1. Text elements")
st.subheader("Different ways to write text")
st.write("`st.write` is the swiss-army knife — it can render text, numbers, dicts, DataFrames, charts, etc.")
st.text("st.text() — plain monospace text, no markdown parsing.")
st.markdown("**st.markdown** supports *markdown*, `code`, and even :rainbow[colors]")
st.caption("st.caption — small grey helper text, good for hints.")
st.code("print('st.code — syntax highlighted block')", language="python")
st.write("Equation can be written as:")
st.latex(r"e^{i\pi} + 1 = 0")
st.divider()