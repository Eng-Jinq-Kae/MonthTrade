import streamlit as st

st.title("Home: SITC Monthly Trade")
st.page_link(
    "app.py",
    label="Go to app Page to know about SITC",
    icon=":material/settings:"
)
st.page_link(
    "pages/2_Table.py",
    label="Go to Table Page",
    icon=":material/table:"
)
st.page_link(
    "pages/3_Prediction Moving Average.py",
    label="Go to Moving Average Page",
    icon=":material/acute:"
)
st.page_link(
    "pages/4_Prediction Linear Regression.py",
    label="Go to Linear Regression Page",
    icon=":material/bolt:"
)