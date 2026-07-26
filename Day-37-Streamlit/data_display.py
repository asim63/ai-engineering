import streamlit as st 
import pandas as pd
import numpy as np

st.header("Displaying data")

df = pd.DataFrame(
    np.random.randn(10, 4),
    columns=["A", "B", "C", "D"]
)

st.subheader("Interactive dataframe")
st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

st.subheader("Static table")
st.table(df.head(3))

m1, m2, m3, m4= st.columns(4)
m1.metric("Temperature", "24°C", "1.2°C")
m2.metric("Humidity", "58%", "-3%")
m3.metric("Users", "1,204", "12")
m4.metric("Haha","404","0%")

st.subheader("Raw JSON")

st.divider()
