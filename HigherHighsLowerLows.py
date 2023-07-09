import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Datamanager.DGMT import DGMT
from Tripple_barrier_method import BackTestSA



class HigherHighsLowerLows(BackTestSA):
    def __init__(self, csv_path, date_col, max_holding, ub_mult=1.005, lb_mult=0.995):
        super().__init__(csv_path, date_col, max_holding, ub_mult, lb_mult)
    

    def generate_signals(self):
        df = self.dmgt.df
        df['longs'] = ((df.high > df.high.shift(1)) & (df.high.shift(1) > df.high.shift(2))
                        & (df.close.shift(2) > df.high.shift(3))) * 1



        df['shorts'] = ((df.low < df.low.shift(1)) & (df.low.shift(1) < df.low.shift(2))
                            & (df.close.shift(2) < df.low.shift(3))) * -1
        


        df['entry'] = df.longs + df.shorts

    # def run_backtest(self):

    #     self.generate_signals()


    #     for row in self.dmgt.df.itertuples():

    #         if row.entry == 1:
    #             if not self.open_pos:
    #                 self.open_long(row.t_plus)
    #             else:
    #                 self.target_price = self.target_price * self.ub_mult
    #                 self.max_holding = self.max_holding + int(self.max_holding_limit/3)
    #                 self.add_zeros()

    #         elif row.entry == -1:
    #             if not self.open_pos:
    #                 self.open_short(row.t_plus)
    #             else:
    #                 self.target_price = self.target_price * self.lb_mult
    #                 self.max_holding = self.max_holding + int(self.max_holding_limit/3)
    #                 self.add_zeros()

    #         elif self.open_pos:
    #             self.monitor_open_positions(row.close, row.Index)
    #         else:
    #             self.add_zeros()

    #     self.add_trade_cols()
        

if __name__ == "__main__":
    m = HigherHighsLowerLows('../ETHUSDT.csv', 'time', 2, ub_mult= 1.02, lb_mult=0.98)
    m.dmgt.recreate_df('240min')
    m.generate_signals()
    m.run_backtest()
    print(abs(m.dmgt.df.direction).sum())


    h = HigherHighsLowerLows('../BTCUSDT.csv', 'time', 2, ub_mult= 1.01, lb_mult=0.99)
    h.dmgt.recreate_df('240min')
    h.generate_signals()
    h.run_backtest()
    print(abs(m.dmgt.df.direction).sum())
    #saved image is inherited run backtest from parent class
    
    plt.plot(h.dmgt.df.index, h.dmgt.df.returns.cumsum(),label='ETH')
    plt.plot(m.dmgt.df.returns.cumsum(), c='red', label='BTC')
    plt.title('Cumulative sum Vs Time')
    plt.xlabel('Time')
    plt.xlabel('Cumulative sum')
    plt.legend()
    plt.show()


