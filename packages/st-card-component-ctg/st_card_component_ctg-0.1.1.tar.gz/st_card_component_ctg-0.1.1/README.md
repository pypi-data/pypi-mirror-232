# streamlit-custom-component

Streamlit component that provides a template to create custom cards

## Installation instructions

```sh
pip install st-card-component-ctg
```

## Usage instructions

```python
# Example Streamlit app

import streamlit as st
from st_card_component_ctg import st_card_component

st.subheader("Test Application!")
st.markdown("---")

st_card_component(
    title="Test title",
    subtitle="A subtitle",
    body="Example body of text",
    link="https://chaancegraves.com"
)
```