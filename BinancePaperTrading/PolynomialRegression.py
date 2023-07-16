import pandas as pd
from datetime import datetime as dt
import numpy as np
from BaseStrategy import BaseStrategy
import json
import time



with open('BinancePaperTrading/Auth.json') as j:
    creds = json.load(j)


client_id = creds['client_id']
client_secret = creds['client_secret']


class PolynomialRegression(BaseStrategy):
    def __init__(self, client_id, client_secret, instrument_name, 
                 max_holding, ub_mult, lb_mult, timeframe,  duration, entry_mask,
                 lookback, n) -> None:
        super().__init__(client_id, client_secret, instrument_name, 
                         max_holding, ub_mult, lb_mult, timeframe, duration)



        self.lookback = lookback
        self.n = n
        self.duration = duration

        self.data_to_save = {"time":dt.now(),"pred":None,"last":None}
        self.entry_mask = entry_mask
        self.delta = 60_000 * 500

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
        print(f"pred: {int(pred[-1])}, last: {int(y[-1][0])}")
        self.data_to_save.update({
                        "time":dt.now(),
                        "pred":int(pred[-1]),
                        "last": y[-1][0]
                        })
        if (pred[-1] / y[-1][0] - 1) > self.entry_mask:
            return 1
        elif (pred[-1] / y[-1][0] - 1) < -self.entry_mask:
            return -1
        else:
            return 0
        
    def get_data(self):
        self.binance.get_klines_hourly(self.instrument, self.duration)
        json_resp = self.binance.df
        if 'close' not in json_resp.columns:
            print('ERR: in get_data PolynomialRegression.py')
            return False, False
        elif 'close' in json_resp.columns:
            data = self.binance.df
            return True, data
        else:
            return False, False

    def run_backtest(self, endtime):
        print(f"started strategy at {dt.now()}")
        while True:
            timenow = dt.now()

            data = self.data_to_save
            df = pd.DataFrame(data, index=["time"])


            df.to_csv('current_time_ETH.csv', index=False)
            if timenow.minute==0 and timenow.second == 0:
                err = True
                while err == True:
                    try:
                        print('Checking...')
                        print(timenow)
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
                        err = False
                        time.sleep(60)

                    except Exception as e:
                        err = True
                        print('ERR: ', e)
                        time.sleep(5)

                time.sleep(1)

                if timenow >= endtime:
                    print(f"Exiting strategy at {dt.now()}")
                    if self.open_pos:
                        self.close_pos()
                    break



if __name__ == '__main__':
    instrument = 'ETHBUSD'
    timeframe = '30'
    ub_mult = 1.02
    lb_mult = 0.98
    max_holding = 24
    entry_cond = 0.05
    n = 4
    lookback = 48
    duration = '3 days ago UTC'

    strat = PolynomialRegression(client_id = client_id, client_secret = client_secret, instrument_name = instrument, 
                                 timeframe=timeframe,
                     max_holding = max_holding, ub_mult = ub_mult, lb_mult = lb_mult, 
                     entry_mask = entry_cond, lookback = lookback, n = n, duration = duration)

    endtime = dt(2024, 7, 14, 21, 30)

    strat.run_backtest(endtime)