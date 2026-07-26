import streamlit as st
from PIL import Image
import time

st.set_page_config(
    page_title="Streamlit Beginner Dashboard",
    layout="wide"
)
if "counter" not in st.session_state:
    st.session_state.counter = 0
    
st.sidebar.title("Sidebar")

page = st.sidebar.radio(
    "Choose a section",
    ["Home", "Profile", "Statistics"]
)
st.sidebar.markdown("---")
name = st.sidebar.text_input("Your Name")
age = st.sidebar.slider("Age", 10, 80, 20)
st.sidebar.markdown("---")
if st.sidebar.button("Increase Counter"):
    st.session_state.counter += 1

st.sidebar.write(f"Counter = {st.session_state.counter}")

if page == "Home":
    st.title("My Dashboard")

    st.header("Welcome")
    st.subheader("Hi this is me Asim")
    st.write(
        "This application demonstrates multiple Streamlit components."
    )

    st.markdown("""
    ### Things Included
    - Sidebar
    - Images
    - Containers
    - Expanders
    - Tabs
    - Session State
    - Columns
    """)

    st.success("Everything is working perfectly!")
    st.warning("This is only a practice application.")
    st.info("Experiment by changing values.")
    st.error("This is how an error message looks.")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Users", "1,245")

    with col2:
        st.metric("Courses", "18")

    with col3:
        st.metric("Rating", "4.8 ⭐")

    st.divider()
    st.header("Image Example")

    try:
        image = Image.open("image.png")
        st.image(image, caption="Local Image", use_container_width=True)
    except:
        st.info("Place an image named image.jpg beside this script.")

    st.divider()

    with st.container(border=True):
        st.subheader("Container Example")

        st.write(
            "Containers help group related components together."
        )

        if st.button("Click Me"):
            st.success("Button clicked!")

    st.divider()

    with st.expander("Click to reveal hidden content"):

        st.write("This content is hidden until expanded.")

        st.code("""
def hello():
    print("Hello Everyone")
        """, language="python")

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        ["Python", "Streamlit", "About"]
    )

    with tab1:
        st.header("Python")
        st.write("Python is simple and beginner friendly.")

    with tab2:
        st.header("Streamlit")
        st.write("Streamlit makes web apps using only Python.")

    with tab3:
        st.header("About")
        st.write("Tabs separate related information neatly.")

elif page == "Profile":

    st.title("User Profile")

    st.write(f"Name : **{name if name else 'Guest'}**")
    st.write(f"Age : **{age}**")

    st.divider()

    if st.button("Save Profile"):
        st.success("Profile saved successfully!")

else:
    st.title("Statistics")
    st.write("Session Counter")
    st.metric("Counter", st.session_state.counter)
    st.divider()
    st.subheader("Loading Example")
    progress = st.progress(0)
    for i in range(101):
        time.sleep(0.02)
        progress.progress(i)

    st.success("Completed!")
    st.divider()
    st.write("Session State Value")
    st.code(f"""
Counter = {st.session_state.counter}
""")