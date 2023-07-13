import pandas as pd
from datetime import datetime as dt
import numpy as np
from BaseStrategy import BaseStrategy
import json


class PolynomialRegression(BaseStrategy):
    def __init__(self, client_id, client_secret, instrument_name, 
                 max_holding, ub_mult, lb_mult, timeframe, trade_capital,
                 date_col,
                 lookback, look_ahead, long_thres, short_thres) -> None:
        super().__init__(client_id, client_secret, instrument_name, 
                         max_holding, ub_mult, lb_mult, timeframe, trade_capital)


        self.date_col = date_col
        self.lookback = lookback
        self.look_ahead = look_ahead
        self.long_thresh = long_thres
        self.short_thresh = short_thres



        self.entry_mask = 0

        self.df = pd.DataFrame()



    def rolling_tt(self ,series):
        '''

        :param series: close price for eth/btc in pandas series
        :param n: lookahead from constructor
        :return: prediction for close_{+n}
        '''

        y = series.values.reshape(-1, 1)
        t = np.arange(len(y))
        X = np.c_[np.ones_like(y), t, t ** 2]
        betas = np.linalg.inv(X.T @ X) @ X.T @ y
        new_vals = np.array([1, t[-1]+self.n, (t[-1]+self.n)**2])
        pred = new_vals@betas  # beta0 + beta1 * t[-1]+n + beta2 * (t[-1]+n)**2
        print(f"pred: {int(pred)}, last: {int(y[-1])}")
        if (pred/y[-1] - 1) > self.entry_mask:
            return 1
        elif (pred/y[-1] -1) < self.entry_mask:
            return -1
        else:
            return 0

    def run_backtest(self, df):
        df = self.rolling_tt()
        for row in df:
            if row.entry == 1 and self.open_pos is False:
                self.open_long()
            elif row.entry == -1 and self.open_pos is False:
                self.open_short()
            elif self.open_pos:
                self.monitor_position()
            



with open('BinancePaperTrading/Auth.json') as j:
    creds = json.load(j)

client_id = creds["paper"]["client_id"]
client_secret = creds["paper"]["client_secret"]


PolynomialRegression(client_id,client_secret, "BTC-PERPETUAL", 12, 1.02,
                     0.98, "1h", 300, "time", 24, 4, 0.03, -0.03)