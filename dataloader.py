from sqlalchemy import text, create_engine
import requests
import pprint
import pandas as pd
from datetime import datetime
from typing import Literal, List, Union
import numpy as np
from sklearn.linear_model import LinearRegression

ENABLE_DB_SETUP = 0 # 1: Setup database data from URL, 0: Read from SQL
ENABLE_DB_CONNECTION = True
ENABLE_DB_SAVE = False

# TODO: when update actual, auto update moving average

engine = create_engine(
    "postgresql+psycopg2://mthtradeuser:123@localhost:5432/MthTrade"
)

sql_read_ref_section = text("""
    SELECT * FROM "RefSection"
""")

sql_read_data_monthtrade = text("""
    SELECT * FROM "DataMonthTrade"
    ORDER BY "Section", "Date"
""")

sql_read_data_monthtrade_section = text("""
    SELECT * FROM "DataMonthTrade"
    WHERE "Section" = :section
""")


def read_ref_section():
    with engine.connect() as conn:
        df = pd.read_sql(sql_read_ref_section, conn)
        if ENABLE_DB_CONNECTION and len(df)>0:
            print("Postgre Db is connected succesfully to RefSection")
    return df


def read_data_monthtrade():
    with engine.connect() as conn:
        df = pd.read_sql(sql_read_data_monthtrade, conn)
        if ENABLE_DB_CONNECTION and len(df)>0:
            print("Postgre Db is connected succesfully to DataMonthTrade")
    return df


def read_data_monthtrade_section(section):
    with engine.connect() as conn:
        df = pd.read_sql(
            sql_read_data_monthtrade_section,
            conn,
            params={"section": section}
        )
        if ENABLE_DB_CONNECTION and len(df) > 0:
            print("Postgre DB connected successfully to DataMonthTrade")
    return df


def save_into_database(df_to_save: pd.DataFrame, table_name):
    if ENABLE_DB_SAVE:
        print(f"Writing into {table_name}...")
        df_to_save.to_sql(
            name=f"{table_name}",
            con=engine,
            schema="public",          # optional if public
            if_exists="append",        # append new rows
            index=False,               # don't write DataFrame index
            method="multi"             # faster insert
        )
    else:
        print("Database save is not enabled.")


def request_url_data_mthtrade():
    print("Get data from URL.")
    url = "https://api.data.gov.my/data-catalogue?id=trade_sitc_1d" 
    response_json = requests.get(url=url).json()
    # pprint.pprint(response_json) #response as json
    # Preprocessing
    df = pd.DataFrame(response_json)
    # Data type preprocessing
    if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'])
    df["exports"] = df["exports"].round().astype("int64")
    df["imports"] = df["imports"].round().astype("int64")
    df = df.rename(columns={
        'date'   : 'Date',
        'section': 'Section',
        'exports': 'Exports',
        'imports': 'Imports'
    })
    return df


def get_data_monthtrade():
    print("Get data from SQL.")
    df = read_data_monthtrade()
    if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'])
    df = df[['Date', 'Section', 'Exports', 'Imports']]
    return df


def data_mthtrade_preprocessing(df: pd.DataFrame, trade: Literal['Exports', 'Imports']):
    df_trade = df[['Date', 'Section', trade]]
    df_trade = df_trade.sort_values(by=['Section','Date']).reset_index(drop=True)
    df_trade = df_trade[df_trade['Section'] != 'overall']
    return df_trade


def setup_moving_average(df_trade, trade: Literal['Exports', 'Imports']):
    export_grouper = df_trade.groupby('Section')[trade]
    if trade == 'Exports':
        df_trade_collect = df_trade.assign(
            Exports_4m = export_grouper.transform(lambda x: x.rolling(window=4,closed='left').mean().round().astype("Int64")),
            Exports_3m = export_grouper.transform(lambda x: x.rolling(window=3,closed='left').mean().round().astype("Int64")),
            Exports_2m = export_grouper.transform(lambda x: x.rolling(window=2,closed='left').mean().round().astype("Int64")),
            Exports_1m = export_grouper.transform(lambda x: x.rolling(window=1,closed='left').mean().round().astype("Int64"))
        )
    else:
        df_trade_collect = df_trade.assign(
            Imports_4m = export_grouper.transform(lambda x: x.rolling(window=4,closed='left').mean().round().astype("Int64")),
            Imports_3m = export_grouper.transform(lambda x: x.rolling(window=3,closed='left').mean().round().astype("Int64")),
            Imports_2m = export_grouper.transform(lambda x: x.rolling(window=2,closed='left').mean().round().astype("Int64")),
            Imports_1m = export_grouper.transform(lambda x: x.rolling(window=1,closed='left').mean().round().astype("Int64"))
        )
    return df_trade_collect


def setup_linear_regression(df_trade, trade: Literal['Exports', 'Imports']):
    unique_section = df_trade['Section'].unique().tolist()
    unique_date = df_trade['Date'].unique().tolist()
    df_trade_pred_frame = []
    for section in unique_section:
        for date in unique_date[3:-1]:
            df_trade_section = df_trade[df_trade['Section']==section]
            df_trade_section = df_trade_section[df_trade_section['Date']<=date].sort_values('Date')
            dates = pd.to_datetime(df_trade_section['Date'])
            X = ((dates.dt.year * 12 + dates.dt.month)
                .values
                .reshape(-1, 1))
            y = df_trade_section[trade] 
            window = 4
            X_win = X[-window:]
            y_win = y[-window:]
            model = LinearRegression()
            model.fit(X_win, y_win)
            last_date = pd.to_datetime(df_trade_section['Date']).max()
            next_date = last_date + pd.offsets.MonthBegin(1)
            X_next = np.array(
                [(next_date.year * 12 + next_date.month)]
            ).reshape(-1, 1)
            y_next = model.predict(X_next)
            df_prediction = pd.DataFrame({
                'Date': [next_date],
                'Section': [section],
                f'{trade}_pred': pd.Series(y_next).round().astype('Int64')
            })
            df_trade_pred_frame.append(df_prediction)
    df_trade_lr = pd.concat(df_trade_pred_frame, ignore_index=True)
    return df_trade_lr


def setup_data_mthtrade_db():
    df = request_url_data_mthtrade()
    save_into_database(df, "DataMonthTrade") # TODO: always uncomment
    return df


def setup_data_ma_pred_db(df_trade, trade: Literal['Exports', 'Imports']):
    df_trade_collect = setup_moving_average(df_trade, trade)
    df_trade_lr = setup_linear_regression(df_trade, trade)
    df_setup_trade = pd.merge(df_trade_collect, df_trade_lr, on=['Date', 'Section'])
    df_setup_trade = df_setup_trade[['Date','Section',f'{trade}_4m',f'{trade}_3m',f'{trade}_2m',f'{trade}_1m',f'{trade}_pred']]
    if trade == 'Exports':
        db_table = "DataMonthTradeExportsPred"
    elif trade == 'Imports':
        db_table = "DataMonthTradeImportsPred"
    else:
        db_table = None
    save_into_database(df_setup_trade, db_table)


def update_data_mthtrade_db(df=None):
    if df is None:
        df = request_url_data_mthtrade()
    df_db = get_data_monthtrade()
    if df_db is None or df_db.empty:
        # DB empty → insert everything
        df_new_data = df.copy()
    else:
        max_db_date = pd.to_datetime(df_db['Date']).max()
        df_new_data = df[df['Date'] > max_db_date]
    if len(df_new_data)>0:
        print("New update data mthtrade coming in.")
        table_name = "DataMonthTrade"
        save_into_database(df_new_data, table_name)
    else:
        print("You are on the latest data.")


# test main
print("Start test dataloader.")
df = None

if ENABLE_DB_SETUP:
    df = setup_data_mthtrade_db()
    # Set up export
    print("Start setting up export...")
    df_exports = data_mthtrade_preprocessing(df, 'Exports')
    setup_data_ma_pred_db(df_exports, 'Exports')
    print("Done setting up export !")
    # Set up import
    print("Start setting up import...")
    df_imports = data_mthtrade_preprocessing(df, 'Imports')
    setup_data_ma_pred_db(df_imports, 'Imports')
    print("Done setting up import !")

update_data_mthtrade_db(df) #TODO always uncomment
df = get_data_monthtrade()
print(df.head())

# section = 'overall'
# df = read_data_monthtrade_section(section)
# print(df)

print("End test dataloader.")