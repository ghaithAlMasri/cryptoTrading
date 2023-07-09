from Tripple_barrier_method import BackTestSA
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import colorama
from colorama import Fore
from Clean_data import Cleandata

class MovingAverageStrategy(BackTestSA):

    def __init__(self, dataframe, max_holding):
        super().__init__(dataframe, max_holding)



    def generate_signals(self):

        df = self.df

        df['ma_20'] = df.close.rolling(20).mean()
        df['ma_50'] = df.close.rolling(50).mean()

        df['ma_diff'] = df.ma_20 - df.ma_50

        df['longs'] = ((df.ma_diff > 0) & (df.ma_diff.shift(1) < 0))*1
        df['shorts'] = ((df.ma_diff < 0) & (df.ma_diff.shift(1) > 0)) * -1

        df['entry'] = df.longs + df.shorts

        self.df = df


    def show_performace(self):
        rets = np.array(self.returns_series)

        cum_rets = rets.cumsum()
        print(Fore.RED ,f'Initial account: $100, maximum reached: {max(cum_rets)*100}, minimum reached:{min(cum_rets)*100}', )
        plt.plot(self.df.time, cum_rets)
        plt.title('Cumulative sum vs Time')
        plt.xlabel('Time')
        plt.ylabel('Cumulative sum')
        plt.show()



if __name__ == '__main__':
    df = Cleandata('/Users/ghaithalmasri/Desktop/fullstackroad/BTCUSDT.csv', 'BTCUSDT').retdf()

    max_holding = 180

    m = MovingAverageStrategy(df, max_holding)

    m.run_backtest()
    m.show_performace()