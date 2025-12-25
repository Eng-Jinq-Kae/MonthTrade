import streamlit as st
import pipeline as pl

def read_df(df, subheader, warning=None):
    st.subheader(subheader)
    if df is None and 'MA Date mismatch' in warning:
        st.warning(body=warning, icon=":material/warning:")
    else:
        st.dataframe(df, hide_index=True)
    st.divider()


st.title("Prediction")
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
    
    subheader = "Prediction Moving Average Export"
    read_df(df_trade_avg_ex, subheader, warning_ma_ex)
    
    subheader = "Prediction Linear Regression Export"
    read_df(df_trade_lr_ex, subheader)
    
    subheader = "Prediction Moving Average Import"
    read_df(df_trade_avg_im, subheader, warning_ma_im)
    
    subheader = "Prediction Linear Regression Import"
    read_df(df_trade_lr_im, subheader)