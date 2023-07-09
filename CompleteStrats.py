import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Tripple_barrier_method import BackTestSA
from HigherHighsLowerLows import HigherHighsLowerLows
from MeanReversion import MeanReversion
from RsiEma import RsiEma


if __name__ == "__main__":
    r = RsiEma('../BTCUSDT.csv','time', max_holding= 12, rsi_window= 14, rsi_long=30, rsi_short=70,
              ma_long=200, ma_short=50, ub_mult=1.01, lb_mult=0.99)
    r.dmgt.recreate_df('10min')
    r.generate_signals()
    r.run_backtest()




    h = HigherHighsLowerLows('../BTCUSDT.csv', 'time', 2, ub_mult=1.02, lb_mult=0.98)
    h.dmgt.recreate_df('240min')
    h.generate_signals()
    h.run_backtest()


    csv_path = "../BTCUSDT.csv" 
    date_col = 'time'
    max_holding = 50
    ub_mult = 1.01
    lb_mult = 0.99 
    up_filter = 1.03 
    down_filter = 0.97

    long_lookback = 60*24*30
    short_lookback = 60*24

    mv = MeanReversion(csv_path, date_col, max_holding, ub_mult,
                         lb_mult, up_filter, down_filter, long_lookback, short_lookback)
    mv.run_backtest()


    total_trades = abs(r.dmgt.df.direction).sum()+abs(h.dmgt.df.direction).sum()+abs(mv.dmgt.df.direction).sum()
    r_returns = r.dmgt.df['returns']
    h_returns = h.dmgt.df['returns']
    mv_returns = mv.dmgt.df['returns']
    
    df = pd.concat([r_returns, h_returns, mv_returns], axis=1, keys=['RsiEma', 'HigherHighsLowerLows', 'MeanReversion'])
    df.fillna(0, inplace=True)
    cumulative_sum = df.RsiEma + df.HigherHighsLowerLows + df.MeanReversion


    cumulative_max = cumulative_sum.cummax()
    drawdown = cumulative_sum - cumulative_max
    max_drawdown = drawdown.min()
    print('Max DDown: ', max_drawdown)

    print('Total Trades: ', total_trades)



    plt.style.use('ggplot')
    plt.figure()
    cumulative_sum.cumsum().plot()
    plt.title('Cumulative sum vs Time')
    plt.xlabel('Time')
    plt.ylabel('Cumulative sum')
    plt.legend()
    plt.show()