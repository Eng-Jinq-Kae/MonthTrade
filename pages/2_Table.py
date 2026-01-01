import streamlit as st
import dataloader as dl

st.title("Table")
df_ref = dl.read_ref_section()
df = dl.update_data_mthtrade_db()
section_list = df_ref['Section'].unique().tolist()
for section in section_list:
    section_name = df_ref.loc[df_ref['Section'] == section, 'SectionName'].iloc[0]
    st.subheader(f'{section} - {section_name}')
    df_section = df[df['Section'] == section]
    df_section_show = df_section.rename(columns={"Exports": "Exports (RM)", "Imports": "Imports (RM)"})
    # st.dataframe(df_section_show, hide_index=True)
    st.dataframe(
        df_section_show.style.format({
            "Exports (RM)": "{:,}",
            "Imports (RM)": "{:,}"
        }),
        hide_index=True
    )
    df_plot = df_section.set_index('Date')[['Exports', 'Imports']]
    st.line_chart(df_plot, color=('#FF7F0E','#1F77B4'))
    st.write(f'Chart of: {section_name}')
    st.divider()

st.success("All table loaded successfully.")