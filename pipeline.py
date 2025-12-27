import dataloader as dl
import numpy as np
import pandas as pd
from typing import Literal, List, Union
from sklearn.linear_model import LinearRegression

LR_WINDOW = 4
READ_URL_SQL = 0 #TODO: suppose to read from url, always=1

def prediction(target_month, target_year):
    target_month_year = pd.Period(f'{target_year}-{target_month}', freq="M").to_timestamp(how='start')

    if READ_URL_SQL:
        df_url = dl.update_data_mthtrade_db()
        df = df_url
    else:
        df = dl.get_data_monthtrade_db()

    df_exports = dl.data_mthtrade_preprocessing(df, 'Exports')
    df_trade_avg_ex, df_trade_lr_ex, warning_ma_ex = prediction_process(target_month_year, df_exports, 'Exports')

    df_imports = dl.data_mthtrade_preprocessing(df, 'Imports')
    df_trade_avg_im, df_trade_lr_im, warning_ma_im =  prediction_process(target_month_year, df_imports, 'Imports')

    return df_trade_avg_ex, df_trade_lr_ex, df_trade_avg_im, df_trade_lr_im, warning_ma_ex, warning_ma_im


def month_year_ma_check(df:pd.DataFrame):
    if df.empty:
        return False
    db_max_month_year = dl.check_db_max_date(df)
    # must be exactly next month
    expected_month_year = db_max_month_year + pd.offsets.MonthBegin(1)
    return db_max_month_year, expected_month_year


def prediction_process(target_month_year, df_trade:pd.DataFrame, trade:Literal['Exports', 'Imports']):
    warning_ma = None
    max_month_year, expected_month_year = month_year_ma_check(df_trade)
    if target_month_year <= expected_month_year:
        df_trade_avg = prediction_moving_average(target_month_year, df_trade, trade)
    else:
        warning_ma = f"""
        MA Date mismatch:\n
        Target date is {target_month_year},\n
        Db date is {max_month_year},\n
        Expect date is {expected_month_year}.\n
        User can only predict moving average offset one month.
        """
        # print(f"MA Date mismatch: Target date_{target_month_year}, Db date_{max_month_year}, Expect date_{expected_month_year}")
        # print(f"MA Date mismatch: User can only predict moving average offset one month")
        print(warning_ma)
        df_trade_avg = None
    df_trade_lr = prediction_linear_regression(target_month_year, df_trade, trade)
    return df_trade_avg, df_trade_lr, warning_ma


def prediction_moving_average(target_month_year, df_trade, trade):
    df_trade = df_trade[df_trade['Date']<target_month_year].sort_values('Date')
    df_last_4 = df_trade.sort_values('Date').groupby('Section').tail(4)
    df_last_4 = df_last_4.sort_values(by=['Section','Date']).reset_index(drop=True)
    df_trade_avg_frame = []
    for section, v in df_last_4.groupby('Section'):
        v = v.sort_values('Date')
        last_date = v['Date'].iloc[-1]
        next_date = last_date + pd.offsets.MonthBegin(1)

        df_trade_avg_frame.append({
            'Date': next_date,
            'Section': section,
            # f'{trade}': pd.NA,  # no actual value yet
            f'{trade}_4m': v[f'{trade}'].tail(4).mean().round(),
            f'{trade}_3m': v[f'{trade}'].tail(3).mean().round(),
            f'{trade}_2m': v[f'{trade}'].tail(2).mean().round(),
            f'{trade}_1m': v[f'{trade}'].tail(1).mean().round()
        })
    # convert to DataFrame
    df_trade_avg = pd.DataFrame(df_trade_avg_frame)
    for col in [f'{trade}_4m',f'{trade}_3m',f'{trade}_2m',f'{trade}_1m']:
        df_trade_avg[col] = df_trade_avg[col].astype('Int64')
    if trade == 'Exports':
        db_table = "DataMonthTradeExportsPred"
    elif trade == 'Imports':
        db_table = "DataMonthTradeImportsPred"
    else:
        db_table = None
    dl.save_into_database(df_trade_avg, db_table)
    return df_trade_avg


def prediction_linear_regression(target_month_year, df_trade, trade):
    df_db = dl.read_data_monthtrade()
    db_max_month_year = dl.check_db_max_date(df_db)
    db_max_month_year = pd.Period(db_max_month_year, freq="M").to_timestamp(how='start')
    df_trade = df_trade[df_trade['Date']<target_month_year].sort_values('Date')
    df_trade = df_trade.sort_values(by=['Section','Date']).reset_index(drop=True)
    df_trade_lr_frame = []
    unique_section = df_trade['Section'].unique().tolist()
    for section in unique_section:
        df_trade_section = df_trade[df_trade['Section']==section]
        dates = pd.to_datetime(df_trade_section['Date'])
        X = ((dates.dt.year * 12 + dates.dt.month)
            .values
            .reshape(-1, 1))
        y = df_trade_section[trade] 
        window = LR_WINDOW
        X_win = X[-window:]
        y_win = y[-window:]
        model = LinearRegression()
        model.fit(X_win, y_win)
        # last_date = pd.to_datetime(df_trade_section['Date']).max()
        expect_month_year = db_max_month_year + pd.offsets.MonthBegin(1)
        if target_month_year <= expect_month_year:
            next_date = target_month_year
            X_next = np.array(
                [(next_date.year * 12 + next_date.month)]
            ).reshape(-1, 1)
            y_next = model.predict(X_next)
            df_prediction = pd.DataFrame({
                'Date': [next_date],
                'Section': [section],
                f'{trade}_pred': pd.Series(y_next).round().astype('Int64')
            })
            df_trade_lr_frame.append(df_prediction)
        else:
            target_period = pd.Period(target_month_year, freq='M')
            db_period = pd.Period(db_max_month_year, freq='M')
            gap_months = target_period.ordinal - db_period.ordinal
            for offset_month in range(1, gap_months+1):
                expect_month_year = db_max_month_year + pd.offsets.MonthBegin(offset_month)
                next_date = expect_month_year
                X_next = np.array(
                    [(next_date.year * 12 + next_date.month)]
                ).reshape(-1, 1)
                y_next = model.predict(X_next)
                df_prediction = pd.DataFrame({
                    'Date': [next_date],
                    'Section': [section],
                    f'{trade}_pred': pd.Series(y_next).round().astype('Int64')
                })
                df_trade_lr_frame.append(df_prediction)
    df_trade_lr = pd.concat(df_trade_lr_frame, ignore_index=True)
    for col in [f'{trade}_pred']:
        df_trade_lr[col] = df_trade_lr[col].astype('Int64')
    if trade == 'Exports':
        db_table = "DataMonthTradeExportsPredLR"
    elif trade == 'Imports':
        db_table = "DataMonthTradeImportsPredLR"
    else:
        db_table = None
    dl.save_into_database(df_trade_lr, db_table)
    return df_trade_lr

if __name__ == "__main__":
    prediction(11,2025)