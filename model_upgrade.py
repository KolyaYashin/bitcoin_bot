import datetime as dt
import numpy as np
import pandas as pd
from binance.client import Client
from config import SECRET_KEY, API_KEY
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor


api_key='hKmlFuyZiyNlaN6ARvCKnhF5owS6yrVJolMeSBfThE5Hc6L26aRM2Z3N8EuVQf0y'
secret_key='B4c5Cr9vwsubR19XK05axHk6aSGhnP91GdXLY57LlaYoUNMf4s5egKIHhtgfJYAd'
client = Client(api_key, secret_key)

def extract_data():
    def get_df(interval, weeks):
        df= pd.DataFrame(client.get_historical_klines('BTCUSDT',interval,
                                                    str((dt.datetime.now() - dt.timedelta(weeks=weeks))),
                                                    str((dt.datetime.now()))))

        df.columns=['open_time','open','high','low','close','volume',
                    'close_time','q_vol','trades','taker_buy_volume',
                    'taker_q_volume','ignored']

        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['open_time'] = df.open_time + dt.timedelta(hours=3)
        df = df.set_index('open_time')
        df['trend'] = np.arange(len(df))
        df['time'] = df.index
        df=df.drop('close_time',axis=1)
        df=df.astype(np.float32,errors='ignore')
        return df

    def global_into_local(df5,features):
        local_features = []
        n=len(features)
        for i in range(n):
            local_features.append(pd.Series(index=df5.index))
        for i in df5.index:
            if i.minute>=30:
                for j in range(n):
                    local_features[j][i] = features[j][i.replace(minute=30)]
            else:
                for j in range(n):
                    local_features[j][i] = features[j][i.replace(minute=0)]
        df5['linear'] = local_features[0]
        df5['tree'] = local_features[0]
        df5['seasonal'] = local_features[0]
        df5['day_mean'] = local_features[0]
        df5['day_var'] = local_features[0]
        df5['week_mean'] = local_features[0]
        df5['week_var'] = local_features[0]


    df30 = get_df('30m',18)
    df5 = get_df('5m',2.5)

    df30['trend_2']=df30.trend**2
    df30['trend_3']=df30.trend**3
    df30['trend_4']=df30.trend**4
    X_time_trend=df30[['trend','trend_2','trend_3','trend_4']]
    y=df30['open']
    y_df30 = y.copy()
    lin_model = Ridge(max_iter=5000)
    lin_model.fit(X_time_trend,y)
    linear = pd.Series(lin_model.predict(X_time_trend),index=y.index)

    tree_model = RandomForestRegressor(n_estimators=5,max_depth=5)
    tree_model.fit(X_time_trend,y)
    tree = pd.Series(tree_model.predict(X_time_trend),index=y.index)

    day_mean = y.rolling(window=48).mean()
    day_var = y.rolling(window=48).std()
    week_mean = y.rolling(window=48*7).mean()
    week_var = y.rolling(window=48*7).std()

    time = np.arange(len(y))
    freq=365.25*24
    order=4
    k =  2 * np.pi * (1 / freq) * time
    for i in range(1,order+1):
        df30[f'sin_{i}'] = np.sin(i*k)
        df30[f'cos_{i}'] = np.cos(i*k)

    X_fourier = df30[['sin_1','cos_1','sin_2','cos_2','sin_3','cos_3','sin_4','cos_4']]

    season_model = Lasso()
    season_model.fit(X_fourier,y)
    seasonal = pd.Series(season_model.predict(X_fourier),index=y.index)

    df5 = df5.drop(['high','low','close','volume','q_vol','trades','taker_buy_volume',
                    'taker_q_volume','ignored','trend','time'],axis=1)

    features = [linear,tree,seasonal,day_mean,day_var,week_mean,week_var]

    df5['time'] = np.arange(1,len(df5)+1)
    df5['const'] = np.ones(len(df5))
    global_into_local(df5=df5, features=features)

    X=df5
    dayofmonth = pd.Series(map(lambda x: x.date().day, X.index), index=X.index)
    dayofweek = pd.Series(map(lambda x: x.date().weekday(), X.index), index=X.index)
    hourofday = pd.Series(map(lambda x: x.time().hour, X.index), index=X.index)

    X['day_of_month'] = dayofmonth
    X['day_of_week'] = dayofweek
    X['hour_of_day'] = hourofday
    time = np.arange(len(X))
    freq=365.25*24
    order=4
    k =  2 * np.pi * (1 / freq) * time
    for i in range(1,order+1):
        X[f'sin_{i}'] = np.sin(i*k)
        X[f'cos_{i}'] = np.cos(i*k)

    for i in range(1,72+1):
        X[f'lag_{i}'] = X.open.shift(i)

    X=X.dropna()
    y=X.open
    X=X.drop('open',axis=1)

    best_model = Ridge(alpha=50, max_iter=5000)

    best_model.fit(X,y)
    def get_new(X,y,y_df30):
        _X={}
        _X['trend'] = [(len(y_df30)+1)]
        _X['trend_2'] = [(len(y_df30)+1)**2]
        _X['trend_3'] = [(len(y_df30)+1)**3]
        _X['trend_4'] = [(len(y_df30)+1)**4]
        time=_X['trend'][0]
        freq=365.25*24
        order=4
        k =  2 * np.pi * (1 / freq) * time
        for i in range(1,order+1):
            _X[f'sin_{i}'] = np.sin(i*k)
            _X[f'cos_{i}'] = np.cos(i*k)
        X_new = pd.DataFrame(_X, index=[X.index[-1]+dt.timedelta(minutes=5)])
        X_new['time'] = [X.time.iloc[-1]+1]
        X_new['const'] = [1]
        X_new['linear'] = lin_model.predict(X_new[['trend', 'trend_2', 'trend_3', 'trend_4']])
        X_new['tree'] = tree_model.predict(X_new[['trend', 'trend_2', 'trend_3', 'trend_4']])
        X_new['seasonal'] = season_model.predict(X_new[['sin_1', 'cos_1', 'sin_2', 'cos_2', 'sin_3', 'cos_3', 'sin_4', 'cos_4']])
        X_new = X_new.drop(['trend','trend_2','trend_3', 'trend_4','sin_1', 'cos_1', 'sin_2', 'cos_2', 'sin_3', 'cos_3', 'sin_4', 'cos_4'],axis=1)
        X_new['day_mean'] = y_df30.iloc[-48:].mean()
        X_new['day_var'] = y_df30.iloc[-48:].std()
        X_new['week_mean'] = y_df30.iloc[-48*7:].mean()
        X_new['week_var'] = y_df30.iloc[-48*7:].std()
        X_new['day_of_month'] = [X['day_of_month'].iloc[-1]]
        X_new['day_of_week'] = [X['day_of_week'].iloc[-1]]
        if X.index[-1].minute==55:
            X_new['hour_of_day'] = [X['hour_of_day'].iloc[-1]]
        else:
            X_new['hour_of_day'] = [(X['hour_of_day'].iloc[-1]+1)%24]
        freq = 365.25*24
        order = 4
        time = X.time.iloc[-1]
        k =  2 * np.pi * (1 / freq) * time
        for i in range(1,order+1):
            X_new[f'sin_{i}'] = np.sin(i*k)
            X_new[f'cos_{i}'] = np.cos(i*k)

        for i in range(1,72+1):
            X_new[f'lag_{i}'] = [y.iloc[-i]]
        return X_new

    print(y.tail(10))
    for i in range(6):
        X_new = get_new(X,y,y_df30)
        y_new = pd.Series(best_model.predict(X_new),index=[y.index[-1]+dt.timedelta(minutes=5)])
        X=pd.concat([X,X_new])
        y=pd.concat([y,y_new])
    print(y.tail(10))
    return y