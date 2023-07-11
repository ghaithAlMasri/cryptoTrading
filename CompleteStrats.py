import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Tripple_barrier_method import BackTestSA
from HigherHighsLowerLows import HigherHighsLowerLows
from MeanReversion import MeanReversion
from RsiEma import RsiEma
from PolynomialTimeTrend import PolyTrend

if __name__ == "__main__":

    csv_path = "../ETHUSDT.csv"
    date_col = 'time'
    max_holding = 12
    lookback = 24
    look_ahead = 4
    long_thres = 0.05
    short_thres = -0.05
    ub_mult = 1.02
    lb_mult = 0.98
    long_tp = 1.02
    long_sl = 0.98
    short_tp = 0.98
    short_sl = 1.02

    Poly = PolyTrend(csv_path, date_col, max_holding,
                     lookback, look_ahead, long_thres,
                     short_thres, ub_mult, lb_mult, long_tp,
                     long_sl, short_tp, short_sl)

    Poly.dmgt.change_resolution('60min')
    Poly.run_backtest()


    h = HigherHighsLowerLows('../BTCUSDT.csv', 'time', 2, ub_mult=1.01, lb_mult=0.99)
    h.dmgt.change_resolution('240min')
    h.generate_signals()
    h.run_backtest()



    total_trades = abs(Poly.dmgt.df.direction).sum()+abs(h.dmgt.df.direction).sum()
    h_returns = h.dmgt.df['returns']
    Poly_returns = Poly.dmgt.df['returns']
    
    df = pd.concat([Poly_returns, h_returns], axis=1, keys=['Poly', 'HigherHighsLowerLows'])
    df.fillna(0, inplace=True)
    cumulative_sum = df.Poly + df.HigherHighsLowerLows


    print('Total Trades: ', total_trades)

    print('initial acc: $1000, Final acc ${}'.format(cumulative_sum.cumsum().values[-1] * 1000))

    plt.style.use('ggplot')
    plt.figure()
    cumulative_sum.cumsum().plot()
    plt.title('Cumulative sum vs Time')
    plt.xlabel('Time')
    plt.ylabel('Cumulative sum')
    plt.legend()
    plt.show()