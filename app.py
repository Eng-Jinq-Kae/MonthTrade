import streamlit as st
import dataloader as dl

if __name__ == "__main__":
    st.title("Malaysia Monthly Trade")
    st.subheader("Follow SITC Section")
    st.write("SITC is known as Standard International Trade Classification (SITC) folllowed by 10 category (0-9)")
    df = dl.read_ref_section()
    df = df[df['Section'] != 'overall']
    st.dataframe(df, hide_index=True)