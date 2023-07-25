import datetime as dt
import numpy as np
import pandas as pd
from binance.client import Client
from config import SECRET_KEY, API_KEY
from sklearn.linear_model import Ridge, Lasso
from xgboost import XGBRegressor




def plotMovingAverage(
    series, window
):
    rolling_mean = series.rolling(window=window).mean()
    rolling_variance = series.rolling(window=window).std()
    return rolling_mean, rolling_variance

def check_model_full(model, X, y, X_curr):
    model.fit(X, y)
    y_pred_1 = model.predict(X)
    y_curr = model.predict(X_curr)
    return y_pred_1, y_curr

def fourier_features(X, freq, order=4):
    X_copy = X.copy()
    time = X.trend
    k =  2 * np.pi * (1 / freq) * time
    for i in range(1, order+1):
        X_copy[f'sin_{i}'] = np.sin(i*k)
        X_copy[f'cos_{i}'] = np.cos(i*k)
    return X_copy

def add_lags(X, interval='1h',count=24):
    X_copy = X.copy()
    if interval == '1h':
        for i in range(1,count+1):
            X_copy[f'lag_{i}h'] = y.shift(i)
    elif interval == '30m':
        for i in range(1,2*count+1):
            X_copy[f'lag_{i}'] = y.shift(i)
    return X_copy

def extract_and_fit(interval: str, delta_weeks: int):
    client = Client(API_KEY, SECRET_KEY)
    df= pd.DataFrame(client.get_historical_klines('BTCUSDT',interval,
                                                str((dt.datetime.now() - dt.timedelta(weeks=delta_weeks))),
                                                str((dt.datetime.now()))))
    df.columns=['open_time','open','high','low','close','volume',
            'close_time','q_vol','trades','taker_buy_volume',
                'taker_q_volume','ignored']
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['open_time'] = df.open_time + dt.timedelta(hours=3)
    df = df.set_index('open_time')
    df['const'] = np.ones(len(df))
    df['trend'] = np.arange(len(df))
    df['time'] = df.index
    df=df.drop('close_time',axis=1)
    df=df.astype(np.float32,errors='ignore')
    df['trend_2']=df.trend**2
    df['trend_3']=df.trend**3
    df['trend_4']=df.trend**4
    X_time_trend=df[['trend','trend_2','trend_3','trend_4']]
    X_current = pd.DataFrame({'trend':[len(df)],'trend_2':[(len(df))**2],'trend_3':[(len(df))**3],'trend_4':[(len(df))**4]})
    X_fourier_curr = fourier_features(X_current, 365.25*24).drop(['trend','trend_2','trend_3','trend_4'],axis=1)
    global y
    y=df['open']
    days=7
    mov_av_w, mov_var_w = plotMovingAverage(y,int(48*days))
    days=1
    mov_av_d, mov_var_d = plotMovingAverage(y,int(48*days))
    X=X_time_trend.copy()
    linear, lin_curr = check_model_full(Lasso(max_iter=1000), X_time_trend, y, X_current)
    X['linear_trend'] = linear
    tree, tree_curr = check_model_full(XGBRegressor(n_estimators=2, max_depth=4, learning_rate=1), X_time_trend, y, X_current)
    X['tree_trend'] = tree
    X['trades'] = df.trades
    X_current['linear_trend'] = lin_curr
    X_current['tree_trend'] = tree_curr
    X_current['trades'] = df.trades.mean()
    X['moving_average_weekly'] = mov_av_w
    X_current['moving_average_weekly'] = y[len(y)-48*7:].mean()
    X['moving_average_daily'] = mov_av_d
    X_current['moving_average_daily'] = y[len(y)-48:].mean()
    X['moving_variance_weekly'] = mov_var_w
    X_current['moving_variance_weekly'] = y[len(y)-48*7:].std()
    X['moving_variance_daily'] = mov_var_d
    X_current['moving_variance_daily'] = y[len(y)-48:].std()
    X['time'] = df.time
    X_fourier = fourier_features(X_time_trend, 365.25*24).drop(['trend','trend_2','trend_3','trend_4'],axis=1)
    seasonal, s_curr = check_model_full(Lasso(),X_fourier,y, X_fourier_curr)
    X['seasonal'] = seasonal
    X_current['seasonal'] = s_curr
    dayofmonth = pd.Series(map(lambda x: x.date().day, X.time), index=X.index)
    dayofweek = pd.Series(map(lambda x: x.date().weekday(), X.time), index=X.index)
    hourofday = pd.Series(map(lambda x: x.time().hour, X.time), index=X.index)
    X['day_of_month'] = dayofmonth
    X_current['day_of_month'] = dt.datetime.now().date().day
    X['day_of_week'] = dayofweek
    X_current['day_of_week'] = dt.datetime.now().date().weekday()
    X['hour_of_day'] = hourofday
    X_current['hour_of_day'] = dt.datetime.now().time().hour
    X=add_lags(X)
    for k in range(1,24+1):
        X_current[f'lag_{k}h'] = y[-k]
    best_model = Lasso(alpha=5, max_iter=5000)
    X['y'] = y
    X = X.dropna().drop(['trend_4','time'],axis=1)
    X_current = X_current.drop(['trend_4'],axis=1)
    y = X['y']
    X = X.drop('y',axis=1)
    best_model.fit(X,y)
    """
    print(X.columns)
    print(X_current.columns)
    """
    predicted_value = best_model.predict(X_current)[0]
    return X_current, predicted_value
