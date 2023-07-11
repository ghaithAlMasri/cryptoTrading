import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Tripple_barrier_method import BackTestSA
from HigherHighsLowerLows import HigherHighsLowerLows
from MeanReversion import MeanReversion

class RsiEma(BackTestSA):
    def __init__(self, csv_path, date_col, max_holding , rsi_window, rsi_long, rsi_short, ma_long = 200, ma_short = 50 ,ub_mult = 1.005, lb_mult = 0.995):
        super().__init__(csv_path, date_col, max_holding , ub_mult, lb_mult)

        self.ub_mult = ub_mult
        self.lb_mult = lb_mult


        self.rsi_window = rsi_window
        self.rsi_long = rsi_long
        self.rsi_short = rsi_short


        self.ma_long = ma_long
        self.ma_short = ma_short






    def calculate_rsi(self):
        df = self.dmgt.df
        df['change'] = df.close - df.close.shift(1)
        df['u'] = [x if x > 0 else 0 for x in df.change]
        df['d'] = [abs(x) if x < 0 else 0 for x in df.change]
        df['u'] = df.u.ewm(span=self.rsi_window, min_periods=self.rsi_window-1).mean()
        df['d'] = df.d.ewm(span=self.rsi_window, min_periods=self.rsi_window-1).mean()
        df['rs'] = df.u/df.d
        df['rsi'] = 100 - (100/(1+df.rs))
        self.dmgt.df = df


    def create_ema(self):
        df = self.dmgt.df
        df['long_ema'] = df.close.ewm(span=self.ma_long, min_periods=self.ma_long - 1).mean()
        df['short_ema'] = df.close.ewm(span=self.ma_short, min_periods=self.ma_short - 1).mean()
        self.dmgt.df = df

    def generate_signals(self):
        df = self.dmgt.df
        self.calculate_rsi()
        self.create_ema()
        df['long'] = ((df.short_ema > df.long_ema) & (df.rsi < self.rsi_long)) * 1
        df['short'] = ((df.short_ema < df.long_ema) & (df.rsi > self.rsi_short)) * -1
        df['entry'] = df.long + df.short
        self.dmgt.df.dropna(inplace=True)
        self.dmgt.df = df
    
    def run_backtest(self):

        self.generate_signals()


        for row in self.dmgt.df.itertuples():

            if row.entry == 1:
                if self.open_pos is False:
                    self.open_long(row.t_plus)
                else:
                    self.target_price = self.target_price * self.ub_mult
                    self.max_holding = self.max_holding + int(self.max_holding_limit/3)
                    self.add_zeros()


            elif row.entry == -1:
                if self.open_pos is False:
                    self.open_short(row.t_plus)
                else:
                    self.target_price = self.target_price * self.lb_mult
                    self.max_holding = self.max_holding + int(self.max_holding_limit/3)
                    self.add_zeros()

            elif self.open_pos:
                self.monitor_open_positions(row.close, row.Index)
            else:
                self.add_zeros()

        self.add_trade_cols()
    
    def save_backtest(self, instrument):
        '''

        :param instrument: ETH, BTC for Ethereum and Bitcoin
        saves backtest to our backtests folder
        '''
        strat_name = self.__class__.__name__
        tf = self.dmgt.timeframe
        self.dmgt.df.to_csv(f"data/backtests/{strat_name}_{tf}-{instrument}.csv")





if __name__ == "__main__":
    r = RsiEma('../ETHUSDT.csv','time', max_holding= 12, rsi_window= 14, rsi_long=30, rsi_short=70,
              ma_long=200, ma_short=50, ub_mult=1.01, lb_mult=0.99)
    r.dmgt.change_resolution('15min')
    r.generate_signals()
    r.run_backtest()
    r.show_performance()

    r.save_backtest('ETH')

   