from sqlalchemy import text, create_engine
import requests
import pprint
import pandas as pd
from datetime import datetime

READ_URL_SQL = 0 # 1 from URL, 0 from SQL
ENABLE_DB_CONNECTION = True
SAVE_INTO_DB = False

engine = create_engine(
    "postgresql+psycopg2://mthtradeuser:123@localhost:5432/MthTrade"
)

sql_read_ref_section = text("""
    SELECT * FROM "RefSection"
""")

sql_read_data_monthtrade = text("""
    SELECT * FROM "DataMonthTrade"
    ORDER BY "Date", "Section"
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
    print(f"Writing into {table_name}...")
    df_to_save.to_sql(
        name=f"{table_name}",
        con=engine,
        schema="public",          # optional if public
        if_exists="append",        # append new rows
        index=False,               # don't write DataFrame index
        method="multi"             # faster insert
    )
    return f"Successfully saved data into {table_name}"


def get_data_monthtrade():
    if READ_URL_SQL:
        print("Get data from URL")
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
            'date': 'Date',
            'section': 'Section',
            'exports': 'Exports',
            'imports': 'Imports'
            })
    else:
        print("Get data from SQL")
        df = read_data_monthtrade()
        if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'])
    df = df[['Date', 'Section', 'Exports', 'Imports']]
    # save_into_database(df, "DataMonthTrade")
    return df


def update_data_mthtrade(df: pd.DataFrame):
    now = datetime.now()
    df_new_data = df[
        (df["date"].dt.year == now.year) &
        (df["date"].dt.month >= now.month)
    ]
    if len(df_new_data)>0 and SAVE_INTO_DB:
        table_name = "DataMonthTrade"
        save_into_database(df_new_data, table_name)


# test main
print("Start test dataloader.")
# read_ref_section()

# df = get_data_monthtrade()
# print(df)

section = 'overall'
df = read_data_monthtrade_section(section)
print(df)

# update_data_mthtrade(df)
print("End test dataloader.")