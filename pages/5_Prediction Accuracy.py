import dataloader as dl
import streamlit as st
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error

st.title("Prediction Accuracy - MAPE")
df_ref = dl.read_ref_section()
section_list = df_ref['Section'].unique().tolist()
section_list.remove("overall")
# def accuracy_trade_section(df_trade, trade):
#     for section in section_list:
#         i = 3
#         df_section = df_trade[df_trade['Section']==section]
#         pred_cols = df_section.columns[3:8]
#         for col in pred_cols:
#             y_true = df_section[trade]
#             y_pred = df_section[col]
#             err = mean_absolute_percentage_error(y_true, y_pred)
#             st.write(trade, section, col, err)

def accuracy_trade_section(df_trade, trade):
    results = []

    for section in section_list:
        df_section = df_trade[df_trade['Section']==section]
        pred_cols = df_section.columns[3:8]  # adjust to your prediction columns

        row = {"Section": section}
        for col in pred_cols:
            y_true = df_section[trade]
            y_pred = df_section[col]
            err = mean_absolute_percentage_error(y_true, y_pred)
            row[col] = err
        results.append(row)

    df_err = pd.DataFrame(results)

    last_cols = df_err.columns[-5:]  # prediction columns only

    def highlight_min_max(row):
        styles = [''] * len(row)
        # only apply styling to last_cols
        for col in row.index:
            if col in last_cols:
                if row[col] == row[last_cols].min():
                    styles[row.index.get_loc(col)] = 'color: green; background-color: #d4fcdc'
                elif row[col] == row[last_cols].max():
                    styles[row.index.get_loc(col)] = 'color: red; background-color: #fcd4d4'
        return styles

    st.dataframe(
        df_err.style.format({col: "{:.4f}" for col in last_cols})
                  .apply(highlight_min_max, axis=1),
        hide_index=True
    )

    date_max = dl.check_db_max_date(df_trade)
    month_max = date_max.month             
    year_max = date_max.year  
    # st.write(f"Data loaded until {date_max.strftime('%B %Y')}")
    st.write(f"Data loaded until {month_max}-{year_max}")
    st.divider()


st.subheader('Export')
df_exports = dl.get_data_pred_db('Exports')
accuracy_trade_section(df_exports,'Exports')


st.subheader('Import')
df_imports = dl.get_data_pred_db('Imports')
accuracy_trade_section(df_imports,'Imports')

st.success("Prediction Accuracy completely loaded.")