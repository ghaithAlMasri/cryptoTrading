import pandas as pd
import pandas_ta as ta
from Datamanager.DGMT import DGMT
from Tripple_barrier_method import BackTestSA

class Vwap(BackTestSA):
    def __init__(self, csv_path, date_col, max_holding, ub_mult=1.005, lb_mult=0.995, 
                 rsi_length = 14, bband_length = 14, bband_stdiv = 2.0, backcandles = 15, long_tp = 1.02, long_sl = 0.98, short_tp = 0.98, short_sl = 1.02):
        super().__init__(csv_path, date_col, max_holding, ub_mult, lb_mult)

        self.backcandles = backcandles
        self.max_holding = max_holding
        self.ub_mult = ub_mult
        self.lb_mult = lb_mult
        self.csv_path = csv_path
        self.rsi_length = rsi_length
        self.bband_length = bband_length
        self.bband_stdiv = bband_stdiv


        self.long_tp = long_tp
        self.long_sl = long_sl
        self.short_tp = short_tp
        self.short_sl = short_sl


    def setdf(self):
        df = self.dmgt.df
        df['rsi'] = ta.rsi(df.close, self.rsi_length)
        df['vwap'] = ta.vwap(df.high, df.low, df.close, df.volume)
        bbands = ta.bbands(df.close, self.bband_length, self.bband_stdiv)
        df = df.join(bbands)
        df.drop(columns=['BBM_14_2.0', 'BBB_14_2.0', 'BBP_14_2.0'], inplace=True)
        df.rename(columns = {'BBL_14_2.0':'bbl', 'BBU_14_2.0':'bbu'}, inplace=True)
        df.dropna(inplace=True)
        self.dmgt.df = df


    def vwap_signal(self):
        backcandles = self.backcandles
        df = self.dmgt.df
        print(len(df))
        length = len(df)
        vwap_signal = [0] * len(df)
        for row in range(backcandles , length):
            upt = 1
            dnt = 1
            # print(row)
            for i in range(row - backcandles, row+1):
                if max(df.open[i], df.close[i]) >= df.vwap[i]:
                    dnt = 0
                if min(df.open[i], df.close[i]) <= df.vwap[i]:
                    upt = 0


            if upt == 1 and dnt == 1:
                vwap_signal[row] = 0
            elif upt == 1 and dnt == 0:
                vwap_signal[row] = 1
            elif upt == 0 and dnt == 1:
                vwap_signal[row] = -1

        df['vwap_sig'] = vwap_signal
        self.dmgt.df = df

    def bband_sig(self):
        df = self.dmgt.df
        bbandsig = [0] * len(df)
        n = 0
        for index, row in df.iterrows():

            if (row['close'] < row['bbl']):
                bbandsig[n] = 1
            elif (row['close'] > row['bbu']):
                bbandsig[n] = -1
            else: 
                bbandsig[n] = 0
            n+=1
        df['bbandsig'] = bbandsig
        self.df = df

    def generate_signals(self):

        print('starting setting df')
        self.setdf()
        print('starting vwapsignal')
        self.vwap_signal()
        print('starting bband')
        self.bband_sig()


        df = self.df
        df['long'] = ((df.vwap_sig == 1) & (df.bbandsig == 1) & (df.rsi < 45)) * 1
        df['short'] = ((df.vwap_sig == -1) & (df.bbandsig == -1) & (df.rsi > 55)) * -1
        df['entry'] = df['long'] + df['short']
        self.dmgt.df = df

    
    def save_backtest(self, instrument):
        '''

        :param instrument: ETH, BTC for Ethereum and Bitcoin
        saves backtest to our backtests folder
        '''
        strat_name = self.__class__.__name__
        tf = self.dmgt.timeframe
        self.dmgt.df.to_csv(f"data/backtests/{strat_name}_{tf}-{instrument}.csv")

    def run_backtest(self):
        self.generate_signals()
        for row in self.dmgt.df.itertuples():
            if row.entry == 1:
              
                if self.open_pos is False:
                    #setting the target and stop, see BacktestSA class to see why this works
                    self.ub_mult = self.long_tp
                    self.lb_mult = self.long_sl
                    self.open_long(row.t_plus)
                else:
                    self.monitor_open_positions(row.close, row.Index)
            elif row.entry == -1:
             
                if self.open_pos is False:
                    self.ub_mult = self.short_sl
                    self.lb_mult = self.short_tp
                    self.open_short(row.t_plus)
                else:
                    self.monitor_open_positions(row.close, row.Index)

            elif self.open_pos:
                self.monitor_open_positions(row.close, row.Index)
            else:
                self.add_zeros()

        self.add_trade_cols()


if __name__ == "__main__":

    csv_path = '../BTCUSDT.csv'
    date_col = 'time'
    max_holding = 72
    ub_mult = 1.02
    lb_mult = 0.98


    long_tp = 1.04
    long_sl = 0.98

    short_tp = 0.96
    short_sl = 1.02

    v = Vwap(csv_path=csv_path, date_col=date_col, max_holding = max_holding, 
             ub_mult= ub_mult, lb_mult=lb_mult, long_sl=long_sl, long_tp=long_tp, 
             short_sl=short_sl, short_tp=short_tp)
    v.dmgt.change_resolution('5min')
    v.run_backtest()
    v.show_performance()
    # v.save_backtest('BTC')
    