import streamlit as st
from st_card_component import st_card_component
#from my_component import my_component

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`

st.subheader("Test #1")
# print the test card component
card_1 = st_card_component(
        title="Test title # 1",
        subtitle="A subtitle",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor...",
        link="https://google.com"
)
st.markdown("---")

st.subheader("Test #2")
card_1 = st_card_component(
        title="Test title # 2",
        subtitle="A subtitle",
        body="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor...",
        link="https://google.com"
)
