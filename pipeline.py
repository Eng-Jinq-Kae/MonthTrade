from dataloader import *

def prediction():
    df = get_data_monthtrade()
    update_data_mthtrade_db(df)

    df_exports = data_mthtrade_preprocessing(df, 'Exports')
    prediction_moving_average(df_exports, 'Exports')
    prediction_linear_regression(df_exports, 'Exports')

    df_imports = data_mthtrade_preprocessing(df, 'Imports')
    prediction_moving_average(df_imports, 'Imports')
    prediction_linear_regression(df_imports, 'Imports')


def prediction_moving_average(df_trade, trade: Literal['Exports', 'Imports']):
    df_last_4 = df_trade.sort_values('Date').groupby('Section').tail(4)
    df_last_4 = df_last_4.sort_values(by=['Section','Date']).reset_index(drop=True)
    df_trade_forecast_avg = []
    for section, v in df_last_4.groupby('Section'):
        v = v.sort_values('Date')
        last_date = v['Date'].iloc[-1]
        next_date = last_date + pd.offsets.MonthBegin(1)

        df_trade_forecast_avg.append({
            'Date': next_date,
            'Section': section,
            f'{trade}': pd.NA,  # no actual value yet
            f'{trade}_4m': v[f'{trade}'].tail(4).mean().round(),
            f'{trade}_3m': v[f'{trade}'].tail(3).mean().round(),
            f'{trade}_2m': v[f'{trade}'].tail(2).mean().round(),
            f'{trade}_1m': v[f'{trade}'].tail(1).mean().round()
        })
    # convert to DataFrame
    df_trade_forecast_avg_all = pd.DataFrame(df_trade_forecast_avg)
    for col in [f'{trade}_4m',f'{trade}_3m',f'{trade}_2m',f'{trade}_1m']:
        df_trade_forecast_avg_all[col] = df_trade_forecast_avg_all[col].astype('Int64')
    if trade == 'Exports':
            db_table = "DataMonthTradeExportsPred"
    elif trade == 'Imports':
        db_table = "DataMonthTradeImportsPred"
    else:
        db_table = None
    save_into_database(df_trade_forecast_avg_all, db_table)
    return None


def prediction_linear_regression(df_trade):
    return None