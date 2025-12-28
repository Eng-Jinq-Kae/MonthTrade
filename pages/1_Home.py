import streamlit as st
import dataloader as dl

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

df_ref = dl.read_ref_section()
df_actual = dl.update_data_mthtrade_db()

def write_container(section: int, df_actual, df_ref):
    container = st.container(border=True)

    with container:
        st.write(f"Section {section}")
        # section_name = df_ref.loc[df_ref['Section'] == section, 'SectionName'].iloc[0]
        # st.write(section_name)


section = 'Overall'
st.subheader('Overall')
write_container(section, df_actual, df_ref)

st.subheader('by Section')
row1 = st.columns(5)
row2 = st.columns(5)
all_cols = row1 + row2
for section, col in enumerate(all_cols):
    section = str(section)
    with col:
        write_container(section, df_actual, df_ref)