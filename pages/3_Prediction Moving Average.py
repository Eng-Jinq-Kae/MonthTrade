import streamlit as st
import altair as alt
import pipeline as pl
import dataloader as dl
import pandas as pd
import datetime
import numpy as np

READ_URL_SQL = dl.READ_URL_SQL #TODO: suppose to read from url, always=1

def click_predict(input_month, input_year):
    st.session_state.s_input_month = input_month
    st.session_state.s_input_year = input_year
    st.session_state.run_prediction = True


def read_df_ma(df_trade_pred, subheader, trade, warning=None):
    st.subheader(subheader)
    if df_trade_pred is None and 'MA Date mismatch' in warning:
        st.warning(body=warning, icon=":material/warning:")
    else:
        st.dataframe(df_trade_pred, hide_index=True)
    st.divider()


def chart_df_ma(subheader, df_trade_avg_ex, df_trade_avg_im, warning, inp_month, inp_year, period=None):
    if df_trade_avg_ex is None and 'MA Date mismatch' in warning:
        st.warning(body=warning, icon=":material/warning:")
        st.stop()
    df_merge_trade_ma = pd.merge(df_trade_avg_ex, df_trade_avg_im, on=['Date', 'Section'])
    # df_actual = dl.read_data_monthtrade()
    df_actual = dl.update_data_mthtrade_db()
    target_month_year = pd.Period(f'{inp_year}-{inp_month}', freq="M").to_timestamp(how='start')
    df_actual = df_actual[df_actual['Date']<target_month_year] #TODO: < or <=
    df_last_12 = (
        df_actual
        .sort_values('Date')
        .groupby('Section', as_index=False)
        .tail(12)
        .reset_index(drop=True)
    )
    df_last_12 = df_last_12.sort_values(by=['Section','Date']).reset_index(drop=True)
    df_last_12 = df_last_12[df_last_12['Section'] != 'overall']

    # st.write("MA table",df_merge_trade_ma.shape)
    # st.write("MA table",df_last_12.shape)
    # st.dataframe(df_merge_trade_ma, hide_index=True)
    # st.dataframe(df_last_12, hide_index=True)

    # st.write(period)
    if period is not None:
        df_merge_trade_ma_p = df_merge_trade_ma[['Date','Section',f'Exports_{period}',f'Imports_{period}']]
        st.subheader("Moving Average Table")
        st.dataframe(df_merge_trade_ma_p, hide_index=True)
        # st.dataframe(df_last_12, hide_index=True)
    else:
        st.stop()
    
    # chart
    st.subheader(subheader)
    df_ref = dl.read_ref_section()
    section_list = df_ref['Section'].unique().tolist()
    section_list.remove("overall")
    for section in section_list:
        section_name = df_ref.loc[df_ref['Section'] == section, 'SectionName'].iloc[0]
        st.subheader(f'{section} - {section_name}')
        df_last_12_section = df_last_12[df_last_12['Section'] == section]
        df_merge_trade_ma_p_section = df_merge_trade_ma_p[df_merge_trade_ma_p['Section'] == section]

        df_last_12_section_chart = df_last_12_section.copy()
        df_last_12_section_chart['Type'] = 'Actual'
        df_last_12_section_chart_long = df_last_12_section_chart.melt(
            id_vars=['Date', 'Section', 'Type'],
            value_vars=['Exports', 'Imports'],
            var_name='Trade',
            value_name='Value'
        )

        df_merge_trade_ma_p_section_chart = df_merge_trade_ma_p_section.copy()
        df_merge_trade_ma_p_section_chart['Type'] = 'Prediction'
        df_merge_trade_ma_p_section_chart_long = df_merge_trade_ma_p_section_chart.melt(
            id_vars=['Date', 'Section', 'Type'],
            value_vars=[f'Exports_{period}',f'Imports_{period}'],
            var_name='Trade',
            value_name='Value'
        )
        df_merge_trade_ma_p_section_chart_long['Trade'] = df_merge_trade_ma_p_section_chart_long['Trade'].str.replace(f'_{period}', '')

        df_plot = pd.concat([df_last_12_section_chart_long, df_merge_trade_ma_p_section_chart_long], ignore_index=True)

        chart = alt.Chart(df_plot).mark_line(point=True).encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Value:Q', title='Trade Value'),
            color=alt.Color(
                'Trade:N',
                scale=alt.Scale(
                    domain=['Exports', 'Imports'],
                    range=['#FF7F0E', '#1F77B4']  # orange, blue
                )
            ),
            strokeDash=alt.StrokeDash(
                'Type:N',
                scale=alt.Scale(
                    domain=['Prediction'],
                    range=[[5, 5]]  # solid vs dotted
                ),
                legend=alt.Legend(title="Prediction")
            ),
            tooltip=['Date:T', 'Trade:N', 'Value:Q', 'Type:N']
        ).properties(
            height=400
        )

        st.altair_chart(chart, width='stretch')
        st.divider()

    st.subheader("Last 12 months actual table")
    st.dataframe(df_last_12, hide_index=True)
    
    st.success("All moving average chart generated successfully.")


# st.title("Prediction Moving Average")
# st.subheader("Target Month Year")
# inp_month = st.number_input(label="Month: Press the -+ icon or type by keyboard.",
#                             min_value=1,
#                             max_value=12,
#                             step=1,
#                             icon=":material/calendar_month:")
# inp_year = st.text_input(label="Year: yyyy format type by keyboard.", value="2025")
# predict = st.button("Predict")
# if predict:
#     print("Run predict")
#     inp_month = int(inp_month)
#     inp_year = int(inp_year)
#     df_trade_avg_ex, df_trade_lr_ex, df_trade_avg_im, df_trade_lr_im, warning_ma_ex, warning_ma_im = pl.prediction(inp_month, inp_year)
    
#     # subheader = "Prediction Moving Average Export"
#     # read_df_ma(df_trade_avg_ex, subheader, 'Exports', warning_ma_ex)

#     # subheader = "Prediction Moving Average Import"
#     # read_df_ma(df_trade_avg_im, subheader, 'Exports', warning_ma_im)

#     subheader = "Chart Moving Average"
#     chart_df_ma(subheader, df_trade_avg_ex, df_trade_avg_im, warning_ma_ex, inp_month, inp_year)



st.title("Prediction Moving Average")
st.subheader("Target Month Year")
col_mth, col_year, col_btn_pred = st.columns(3)
current_month = datetime.date.today().month
with col_mth:
    inp_month = st.number_input(label="Month",
                                min_value=1,
                                max_value=12,
                                step=1,
                                value=current_month,
                                icon=":material/calendar_month:")
current_year = datetime.date.today().year
with col_year:
    inp_year = st.number_input(label="Month",
                                min_value=current_year-100,
                                max_value=current_year+100,
                                step=1,
                                value=current_year,
                                icon=":material/calendar_month:")
pred_input = (inp_month, inp_year)
with col_btn_pred:
    col_btn_pred.space("small")
    predict = st.button("Predict", on_click=click_predict, args=pred_input)
# st.session_state
if st.session_state.get("run_prediction", False):
    (
        st.session_state.df_trade_avg_ex,
        st.session_state.df_trade_lr_ex,
        st.session_state.df_trade_avg_im,
        st.session_state.df_trade_lr_im,
        st.session_state.warning_ma_ex,
        st.session_state.warning_ma_im,
    ) = pl.prediction(
        st.session_state.s_input_month,
        st.session_state.s_input_year,
    )

    st.success(f"Date loaded:{st.session_state.s_input_month}-{st.session_state.s_input_year}")

    # subheader = "Prediction Moving Average Export"
    # read_df_ma(st.session_state.df_trade_avg_ex, subheader, 'Exports', st.session_state.warning_ma_ex)

    # subheader = "Prediction Moving Average Import"
    # read_df_ma(st.session_state.df_trade_avg_im, subheader, 'Imports', st.session_state.warning_ma_im)

    subheader = "Chart Moving Average"
    # chart_df_ma(subheader,
    #             st.session_state.df_trade_avg_ex,
    #             st.session_state.df_trade_avg_im,
    #             st.session_state.warning_ma_ex,
    #             st.session_state.s_input_month,
    #             st.session_state.s_input_year)

    period = st.segmented_control(
        label="Moving Average Period",
        options=['4m','3m','2m','1m'],
        default='4m'
    )
    # chart_df_ma(subheader, st.session_state.df_trade_avg_ex, st.session_state.df_trade_avg_im, st.session_state.warning_ma_ex, inp_month, inp_year)
    chart_df_ma(subheader,
                st.session_state.df_trade_avg_ex,
                st.session_state.df_trade_avg_im,
                st.session_state.warning_ma_ex,
                st.session_state.s_input_month,
                st.session_state.s_input_year,
                period)