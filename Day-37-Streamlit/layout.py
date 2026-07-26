import streamlit as st 
st.header("Layout tools")

tab1, tab2, tab3 = st.tabs(["Container", "Expander", "Columns again"])

with tab1:
    container = st.container(border=True)
    container.write("This text is inside a bordered container.")
    st.write("This text is outside the container (written after, but appears where placed in code).")

with tab2:
    with st.expander("Click to expand for more details"):
        st.write("Hidden content revealed! ")
        st.image("image.png")

with tab3:
    left, right = st.columns([2, 1])  # unequal width ratio 2:1
    left.write("Wider column (ratio 2)")
    left.image("image.png")
    right.write("Narrower column (ratio 1)")
    right.image("image2.png")

st.divider()