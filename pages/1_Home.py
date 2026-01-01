import streamlit as st
import dataloader as dl
import pandas as pd

def colored_value(label, current, previous):
    if label == "Exports":
        color = "green" if current >= previous else "red"
    else:
        color = "red" if current >= previous else "green"
    index_change  = (current / previous) - 1
    st.markdown(
        f"**{label}:** <span style='color:{color}'>{current:,} ({index_change:.2f}%)</span>",
        unsafe_allow_html=True
    )


df_ref = dl.read_ref_section()
df_actual = dl.update_data_mthtrade_db()
def write_container(section: int, df_actual, df_ref):
    container = st.container(border=True, width="stretch")
    df_actual = df_actual[df_actual["Section"] == section]

    with container:
        st.write(f"**Section {section}**")
        db_month_year_max = dl.check_db_max_date(df_actual)
        db_month_year_max_1 = db_month_year_max - pd.offsets.MonthBegin(1)
        # st.write(db_month_year_max)
        # st.write(db_month_year_max_1)
        # section_name = df_ref.loc[df_ref['Section'] == section, 'SectionName'].iloc[0]
        # st.write(section_name)

        row = df_actual.loc[df_actual["Date"] == db_month_year_max]
        if not row.empty:
            export_val_last = row["Exports"].iloc[0]
            import_val_last = row["Imports"].iloc[0]
        else:
            st.warning("No data found for this month")

        row = df_actual.loc[df_actual["Date"] == db_month_year_max_1]
        if not row.empty:
            export_val_last1 = row["Exports"].iloc[0]
            import_val_last1 = row["Imports"].iloc[0]
        else:
            st.warning("No data found for this month")
        
        st.write(db_month_year_max.strftime("%B %Y"))
        colored_value("Exports", export_val_last, export_val_last1)
        colored_value("Imports", import_val_last, import_val_last1)
        st.write(db_month_year_max_1.strftime("%B %Y"))
        st.write(f"**Export:** {export_val_last1:,}")
        st.write(f"**Import:** {import_val_last1:,}")


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
    icon=":material/online_prediction:"
)

st.page_link(
    "pages/5_Prediction Accuracy.py",
    label="Go to Prediction Accuracy Page",
    icon=":material/search_gear:"
)


multi = '''
If export more than previous month, it will show :green[green]  
If import more than previous month, it will show :red[red]
'''
st.markdown(multi)

section = 'overall'
st.subheader('Overall')
write_container(section, df_actual, df_ref)

st.subheader('by Section')
row1 = st.columns(2)
row2 = st.columns(2)
row3 = st.columns(2)
row4 = st.columns(2)
row5 = st.columns(2)
all_cols = row1 + row2 + row3 + row4 + row5
for section, col in enumerate(all_cols):
    section = str(section)
    with col:
        write_container(section, df_actual, df_ref)

df_ref = dl.read_ref_section()
df_ref = df_ref[df_ref['Section'] != 'overall']
st.dataframe(df_ref, hide_index=True)

st.success("All table loaded successfully.")