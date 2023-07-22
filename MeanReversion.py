from Tripple_barrier_method import BackTestSA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class IMeanReversion(BackTestSA):

    def __init__(self, csv_path, date_col, max_holding, ub_mult, lb_mult,
                 up_filter, down_filter, long_lookback, short_lookback):

        super().__init__(csv_path, date_col, max_holding)
        #target and stop losses mults
        self.ub_mult = ub_mult
        self.lb_mult = lb_mult
        #conditions
        self.up_filter = up_filter
        self.down_filter = down_filter
        # lookbacks
        self.long_lookback = long_lookback # n
        self.short_lookback = short_lookback # k


    def generate_signals(self):
        df = self.dmgt.df

        df['min_24'] = df.close.rolling(self.short_lookback).min()
        df['max_24'] = df.close.rolling(self.short_lookback).max()

        df['longs'] = ((df.close <= df.min_24) &
                       (df.close > df.close.shift(self.long_lookback)*self.up_filter))*1
        df['shorts'] = ((df.close >= df.max_24) &
                       (df.close < df.close.shift(self.long_lookback) * self.down_filter)) * -1

        df['entry'] = df.longs + df.shorts
        df['entry'] = df.entry.shift(1) #uncomment to shift signal to enter on next close
        df.dropna(inplace=True)



if __name__ == "__main__":
    csv_path = "../BTCUSDT.csv" 
    date_col = 'time'
    max_holding = 200 
    ub_mult = 1.05
    lb_mult = 0.95
    up_filter = 1.1 
    down_filter = 0.9 

    long_lookback = 60*24*30
    short_lookback = 60*24

    Imv = IMeanReversion(csv_path=csv_path, date_col=date_col, max_holding=max_holding, 
                         ub_mult=ub_mult,
                        lb_mult= lb_mult, up_filter=up_filter, down_filter=down_filter, 
                        long_lookback=long_lookback, short_lookback=short_lookback)

    Imv.run_backtest()
    Imv.show_performance()