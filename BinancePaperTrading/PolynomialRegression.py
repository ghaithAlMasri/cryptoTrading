import pandas as pd
from datetime import datetime as dt
import numpy as np
from BaseStrategy import BaseStrategy
import json
import time



with open('BinancePaperTrading/Auth.json') as j:
    creds = json.load(j)


client_id = creds['paper']['client_id']
client_secret = creds['paper']['client_secret']


class PolynomialRegression(BaseStrategy):
    def __init__(self, client_id, client_secret, instrument_name, 
                 max_holding, ub_mult, lb_mult, timeframe, trade_capital,
                 entry_mask,
                 lookback, n) -> None:
        super().__init__(client_id, client_secret, instrument_name, 
                         max_holding, ub_mult, lb_mult, timeframe, trade_capital)



        self.lookback = lookback
        self.n = n




        self.entry_mask = entry_mask
        self.delta = 60_000 *60_000

        self.df = pd.DataFrame()



    def generate_signals(self ,series):
        '''

        :param series: close price for eth/btc in pandas series
        :param n: lookahead from constructor
        :return: prediction for close_{+n}
        '''

        y = series.close.values.reshape(-1, 1)
        t = np.arange(len(y))
        X = np.c_[np.ones_like(y), t, t ** 2]
        betas = np.linalg.inv(X.T @ X) @ X.T @ y
        new_vals = np.array([1, t[-1] + self.n, (t[-1] + self.n) ** 2])
        pred = new_vals @ betas
        print(f"pred: {int(pred)}, last: {int(y[-1])}")

        if (pred / y[-1] - 1) > self.entry_mask:
            return 1
        elif (pred / y[-1] - 1) < -self.entry_mask:
            return -1
        else:
            return 0
        
    def get_data(self):
        end = self.utc_times_now()
        start = end - self.delta * self.lookback
        json_resp = self.derbit.get_klines(self.instrument, start, end, self.timeframe)
        if 'error' in json_resp.keys():
            print(json_resp['error'])
            return False, False
        elif 'result' in json_resp.keys():
            data = self.json_to_df(json_resp)
            return True, data
        else:
            return False, False

    def run_backtest(self, endtime):
        print(f"started strategy at {dt.now()}")
        while True:
            try:
                timenow = dt.now()
                if timenow.minute == 0:
                    t = time.time()
                    good_call, data = self.get_data()
                    if not good_call:
                        time.sleep(1)
                        continue
                    last_price = data.close.values[-1]
                    signal = self.generate_signals(data)

                    if signal == 1 and self.open_pos is False:
                        self.open_long()
                        print(f"took {time.time()-t} seconds to execute")
                    elif signal == -1 and self.open_pos is False:
                        self.open_short()
                        print(f"took {time.time() - t} seconds to execute")
                    elif self.open_pos:
                        self.monitor_position(last_price)
                    else:
                        pass
            except Exception as e:
                print('ERR: ', e)
                time.sleep(5)

            time.sleep(1)

            if timenow >= endtime:
                print(f"Exiting strategy at {dt.now()}")
                if self.open_pos:
                    self.close_pos()
                break



if __name__ == '__main__':
    instrument = 'BTC-PERPETUAL'
    timeframe = '1h'
    trade_capital = 100_000
    ub_mult = 1.02
    lb_mult = 0.98
    max_holding = 12
    entry_cond = 0.05
    n = 4
    lookback = 12

    strat = PolynomialRegression(client_id = client_id, client_secret = client_secret, instrument_name = instrument, timeframe = timeframe, trade_capital = trade_capital,
                     max_holding = max_holding, ub_mult = ub_mult, lb_mult = lb_mult, entry_mask = entry_cond, lookback = lookback, n = n)

    endtime = dt(2024, 7, 14, 21, 30)

    strat.run_backtest(endtime)