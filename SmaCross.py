from Tripple_barrier_method import BackTestSA
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class MovingAverageStrategy(BackTestSA):

    def __init__(self, dataframe_path, date_col, max_holding):
        super().__init__(dataframe_path, date_col, max_holding)



    def generate_signals(self):

        df = self.dmgt.df

        df['ma_20'] = df.close.rolling(20).mean()
        df['ma_50'] = df.close.rolling(50).mean()

        df['ma_diff'] = df.ma_20 - df.ma_50

        df['longs'] = ((df.ma_diff > 0) & (df.ma_diff.shift(1) < 0))*1
        df['shorts'] = ((df.ma_diff < 0) & (df.ma_diff.shift(1) > 0)) * -1

        df['entry'] = df.longs + df.shorts

        self.dmgt.df = df


    def show_performace(self):
        rets = np.array(self.dmgt.df.returns)

        cum_rets = rets.cumsum()

        plt.plot(self.dmgt.df.index, cum_rets)
        plt.title('Cumulative sum vs Time')
        plt.xlabel('Time')
        plt.ylabel('Cumulative sum')
        plt.show()



if __name__ == '__main__':

    max_holding = 10

    m = MovingAverageStrategy('../BTCUSDT.csv', 'time', max_holding)

    m.dmgt.recreate_df('10min')
    print(m.dmgt.df.tail())

    m.run_backtest()
    m.show_performace()