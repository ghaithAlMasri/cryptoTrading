from Tripple_barrier_method import BackTestSA
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MeanReversion(BackTestSA):

    def __init__(self, csv_path, date_col, max_holding, ub_mult, lb_mult,
                 up_filter, down_filter, long_lookback, short_lookback):

        super().__init__(csv_path, date_col, max_holding)

        self.ub_mult = ub_mult
        self.lb_mult = lb_mult

        self.up_filter = up_filter
        self.down_filter = down_filter

        self.long_lookback = long_lookback
        self.short_lookback = short_lookback


    def generate_signals(self):
        df = self.dmgt.df

        df['min_24'] = df.close.rolling(self.short_lookback).min()
        df['max_24'] = df.close.rolling(self.short_lookback).max()

        df['shorts'] = ((df.close <= df.min_24) &
                       (df.close > df.close.shift(self.long_lookback)*self.down_filter)) * -1
        df['longs'] = ((df.close >= df.max_24) &
                       (df.close < df.close.shift(self.long_lookback) * self.up_filter)) * 1

        df['entry'] = df.longs + df.shorts

        df.dropna(inplace=True)

    def save_backtest(self, instrument):
        '''

        :param instrument: ETH, BTC for Ethereum and Bitcoin
        saves backtest to data/backtests folder
        '''
        strat_name = self.__class__.__name__
        tf = self.dmgt.timeframe
        self.dmgt.df.to_csv(f"data/backtests/{strat_name}_{tf}-{instrument}.csv")



if __name__ == "__main__":
    csv_path = "../ETHUSDT.csv" 
    date_col = 'time'
    max_holding = 300
    ub_mult = 1.05
    lb_mult = 0.95 
    up_filter = 1.10
    down_filter = 0.90

    long_lookback = 60*24*30
    short_lookback = 60*24

    Imv = MeanReversion(csv_path, date_col, max_holding, ub_mult,
                         lb_mult, up_filter, down_filter, long_lookback, short_lookback)

    Imv.run_backtest()
    Imv.show_performance()
    Imv.save_backtest('ETH')