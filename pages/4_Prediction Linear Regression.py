import streamlit as st
import pipeline as pl
import dataloader as dl
import pandas as pd

def read_df_lr(df_trade_pred, subheader, trade, warning=None):
    st.subheader(subheader)
    df_actual = dl.read_data_monthtrade()
    df_trade_actual = dl.data_mthtrade_preprocessing(df_actual, trade)
    frames = [df_trade_actual, df_trade_pred]
    df_actual_pred = pd.concat(frames)
    st.dataframe(df_actual_pred, hide_index=True)
    st.divider()


st.title("Prediction Linear Regression")
st.subheader("Target Month Year")
inp_month = st.number_input(label="Month: Press the -+ icon or type by keyboard.",
                            min_value=1,
                            max_value=12,
                            step=1,
                            icon=":material/calendar_month:")
inp_year = st.text_input(label="Year: yyyy format type by keyboard.", value="2025")
predict = st.button("Predict")
if predict:
    inp_month = int(inp_month)
    inp_year = int(inp_year)
    df_trade_avg_ex, df_trade_lr_ex, df_trade_avg_im, df_trade_lr_im, warning_ma_ex, warning_ma_im = pl.prediction(inp_month, inp_year)
    
    subheader = "Prediction Linear Regression Export"
    read_df_lr(df_trade_lr_ex, subheader, 'Exports')
    
    subheader = "Prediction Linear Regression Import"
    read_df_lr(df_trade_lr_im, subheader, 'Exports',)