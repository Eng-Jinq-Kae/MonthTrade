import streamlit as st
import dataloader as dl

st.title("Table")
df = dl.read_ref_section()
section_list = df['Section'].unique().tolist()
for section in section_list:
    section_name = df.loc[df['Section'] == section, 'SectionName'].iloc[0]
    st.subheader(f'{section} - {section_name}')
    df_section = dl.read_data_monthtrade_section(section)
    st.dataframe(df_section, hide_index=True)
    df_plot = df_section.set_index('Date')[['Exports', 'Imports']]
    st.line_chart(df_plot, color=('#FF7F0E','#1F77B4'))
    st.write(f'Chart of: {section_name}')
    st.divider()