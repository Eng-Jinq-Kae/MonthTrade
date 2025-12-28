import streamlit as st
import pipeline as pl
import dataloader as dl
import pandas as pd
import altair as alt
import datetime
import numpy as np

def chart_df_lr(subheader, df_trade_pred_ex, df_trade_pred_im, inp_month, inp_year):
    df_merge_trade_lr = pd.merge(df_trade_pred_ex, df_trade_pred_im, on=['Date', 'Section'])
    df_actual = dl.update_data_mthtrade_db()
    target_month_year = pd.Period(f'{inp_year}-{inp_month}', freq="M").to_timestamp(how='start')
    df_actual = df_actual[df_actual['Date']<target_month_year] # TODO: < or <=
    df_last_12 = (
        df_actual
        .sort_values('Date')
        .groupby('Section', as_index=False)
        .tail(12)
        .reset_index(drop=True)
    )
    df_last_12 = df_last_12.sort_values(by=['Section','Date']).reset_index(drop=True)
    df_last_12 = df_last_12[df_last_12['Section'] != 'overall']
    st.subheader("Linear Regression Table")
    # st.dataframe(df_merge_trade_lr, hide_index=True)
    last_two_cols = df_merge_trade_lr.columns[-2:]
    st.dataframe(
        df_merge_trade_lr.style.format(
            {col: "{:,}" for col in last_two_cols}
        ),
        hide_index=True
    )

    # chart
    st.subheader(subheader)
    st.subheader(subheader)
    df_ref = dl.read_ref_section()
    section_list = df_ref['Section'].unique().tolist()
    section_list.remove("overall")
    for section in section_list:
        section_name = df_ref.loc[df_ref['Section'] == section, 'SectionName'].iloc[0]
        st.subheader(f'{section} - {section_name}')
        df_last_12_section = df_last_12[df_last_12['Section'] == section]
        df_merge_trade_lr_section = df_merge_trade_lr[df_merge_trade_lr['Section'] == section]

        df_last_12_section_chart = df_last_12_section.copy()
        df_last_12_section_chart['Type'] = 'Actual'
        df_last_12_section_chart_long = df_last_12_section_chart.melt(
            id_vars=['Date', 'Section', 'Type'],
            value_vars=['Exports', 'Imports'],
            var_name='Trade',
            value_name='Value'
        )

        df_merge_trade_lr_section_chart = df_merge_trade_lr_section.copy()
        df_merge_trade_lr_section_chart['Type'] = 'Prediction'
        df_merge_trade_lr_section_chart_long = df_merge_trade_lr_section_chart.melt(
            id_vars=['Date', 'Section', 'Type'],
            value_vars=[f'Exports_pred',f'Imports_pred'],
            var_name='Trade',
            value_name='Value'
        )
        df_merge_trade_lr_section_chart_long['Trade'] = df_merge_trade_lr_section_chart_long['Trade'].str.replace(f'_pred', '')

        df_plot = pd.concat([df_last_12_section_chart_long, df_merge_trade_lr_section_chart_long], ignore_index=True)

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
    # st.dataframe(df_last_12, hide_index=True)
    last_two_cols = df_last_12.columns[-2:]
    st.dataframe(
        df_last_12.style.format(
            {col: "{:,}" for col in last_two_cols}
        ),
        hide_index=True
    )
    
    st.success("All linear regression chart generated successfully.")


st.title("Prediction Linear Regression")
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
    # predict = st.button("Predict", on_click=click_predict, args=pred_input)
    predict = st.button("Predict")
if predict:
    inp_month = int(inp_month)
    inp_year = int(inp_year)
    df_trade_avg_ex, df_trade_lr_ex, df_trade_avg_im, df_trade_lr_im, warning_ma_ex, warning_ma_im = pl.prediction(inp_month, inp_year)
    st.success(f"Date loaded:{inp_month}-{inp_year}")
    subheader = "Chart Linear Regression"
    chart_df_lr(subheader, df_trade_lr_ex, df_trade_lr_im, inp_month, inp_year)