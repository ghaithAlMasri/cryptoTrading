import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Datamanager.DGMT import DGMT




class BackTestSA:
    '''
    backtesting class for all single asset strategies,
    columns must include the following :
    close: float
    timestamp: date
    '''

    def __init__(self, csv_path, date_col, max_holding):

        self.DGMT = DGMT(csv_path, date_col)

        # trade variables
        self.open_pos = False
        self.entry_price = None
        self.direction = None
        self.target_price = None
        self.stop_price = None
        # vertical barrier variable
        self.max_holding = max_holding
        self.max_holding_limit = max_holding

        # barrier multipliers
        self.ub_mult = 1.005
        self.lb_mult = 0.995

        # special case of vertical barrier
        self.end_date = self.DGMT.df.index.values[-1]

        self.returns_series = []

    def open_long(self, price):
        '''

        :param price: price we open long at
        :return: populates trade variables from constructor with relevant variables
        '''
        self.open_pos = True
        self.direction = 1
        self.entry_price = price
        self.target_price = price * self.ub_mult
        self.stop_price = price * self.lb_mult
        self.returns_series.append(0)

    def open_short(self, price):
        '''

        :param price: price we open short at
        :return: populates trade variables from constructor with relevant variables
        '''
        self.open_pos = True
        self.direction = -1
        self.entry_price = price
        self.target_price = price * self.lb_mult
        self.stop_price = price * self.ub_mult
        self.returns_series.append(0)

    def reset_variables(self):
        '''
        resets the variables after we close a trade
        '''
        self.open_pos = False
        self.entry_price = None
        self.direction = None
        self.target_price = None
        self.stop_price = None
        self.max_holding = self.max_holding_limit

    def close_position(self, price):
        '''

        :param price: price we are exiting trade at
        :return: appends the trade pnl to the returns series
        and resets variables
        '''
        pnl = (price / self.entry_price - 1) * self.direction
        self.returns_series.append(pnl)
        self.reset_variables()

    def generate_signals(self):
        '''

        use this function to make sure generate signals has been included in the child class
        '''
        if 'entry' not in self.DGMT.df.columns:
            raise Exception('You have not created signals yet')

    def monitor_open_positions(self, price, timestamp):
        # check upper horizontal barrier for long positions
        if price >= self.target_price and self.direction == 1:
            self.close_position(price)
        # check lower horizontal barrier for long positions
        elif price <= self.stop_price and self.direction == 1:
            self.close_position(price)
        # check lower horizontal barrier for short positions
        elif price <= self.target_price and self.direction == -1:
            self.close_position(price)
        # check upper horizontal barrier for short positions
        elif price >= self.stop_price and self.direction == -1:
            self.close_position(price)
        # cehck special case of vertical barrier
        elif timestamp == self.end_date:
            self.close_position(price)
        # check vertical barrier
        elif self.max_holding <= 0:
            self.close_position(price)
        # if all above conditions not true, decrement max holding by 1 and append a zero to returns column
        else:
            self.max_holding = self.max_holding - 1
            self.returns_series.append(0)

    def run_backtest(self):
        # signals generated from child class
        self.generate_signals()

        # loop over dataframe
        for row in self.DGMT.df.itertuples():
            # if we get a long signal and do not have open position open a long
            if row.entry == 1 and self.open_pos is False:
                self.open_long(row.t_plus)
            # if we get a short position and do not have open position open a sort
            elif row.entry == -1 and self.open_pos is False:
                self.open_short(row.t_plus)
            # monitor open positions to see if any of the barriers have been touched, see function above
            elif self.open_pos:
                self.monitor_open_positions(row.close, row.Index)
            else:
                self.returns_series.append(0)

        self.DGMT.df['returns'] = self.returns_series
        self.returns_series = []


class MovingAverageStrategy(BackTestSA):

    def __init__(self, csv_path, date_col, max_holding):
        super().__init__(csv_path, date_col, max_holding)

    def generate_signals(self):
        df = self.DGMT.df

        df['ma_20'] = df.close.rolling(20).mean()
        df['ma_50'] = df.close.rolling(50).mean()

        df['ma_diff'] = df.ma_20 - df.ma_50

        df['longs'] = ((df.ma_diff > 0) & (df.ma_diff.shift(1) < 0)) * 1
        df['shorts'] = ((df.ma_diff < 0) & (df.ma_diff.shift(1) > 0)) * -1

        df['entry'] = df.longs + df.shorts

        self.DGMT.df = df

    def show_performace(self):
        self.DGMT.df.returns.cumsum().plot()
        plt.title(f"Strategy results for {self.DGMT.timeframe} timeframe")
        plt.show()
    '''
    backtesting class for all single asset strategies, 
    columns must include the following :
    close: float
    timestamp: date

    '''

    def __init__(self, dataframe_path, date_col, max_holding):


        #vertical barrier variable
        self.max_holding = max_holding
        self.max_holding_limit = max_holding

        self.DGMT = DGMT(dataframe_path, date_col)
        self.df = self.DGMT.df

        #trade variables
        self.open_pos = False
        self.entry_price = None
        self.direction = None
        self.target_price = None
        self.stop_price = None

        #barrier multipliers
        self.ub_mult = 1.005
        self.lb_mult = 0.995
        
        #special case of vertical barrier

        self.end_date = self.df.index.values[-1]

        self.returns_series = []


    def open_long(self, price):
        '''
        
        :param price: price we open long at
        :return: populates trade variables from constructor with relevant variables

        '''
        self.open_pos = True
        self.direction = 1
        self.entry_price = price
        self.target_price = price * self.ub_mult
        self.stop_price = price * self.lb_mult
        self.returns_series.append(0)

    def open_short(self, price):
        '''
        
        :param price: price we open short at
        :return: populates trade variables from constructor with relevant variables

        '''
        self.open_pos = True
        self.direction = -1
        self.entry_price = price
        self.target_price = price * self.lb_mult
        self.stop_price = price * self.ub_mult
        self.returns_series.append(0)

    def reset_variables(self):
        '''
        resets the variables after we close a trade

        '''
        self.open_pos = False
        self.entry_price = None
        self.direction = None
        self.target_price = None
        self.stop_price = None
        self.max_holding = self.max_holding_limit

    def close_position(self, price):
        '''
        
        :param price: price we are exiting trade at 
        :return: appends the trade pnl to the returns series 
        and resets variables 

        '''
        pnl = (price/self.entry_price-1)*self.direction
        self.returns_series.append(pnl)
        self.reset_variables()


    def generate_signals(self):
        '''
        
        use this function to make sure generate signals has been included in the child class 
        
        '''
        if 'entry' not in self.DGMT.df.columns:
            raise Exception('You have not created signals yet')



    def monitor_open_positions(self, price, time):
        #check upper horizontal barrier for long positions
        if price >= self.target_price and self.direction == 1:
            self.close_position(price)
        #check lower horizontal barrier for long positions
        elif price <= self.stop_price and self.direction == 1:
            self.close_position(price)
        # check lower horizontal barrier for short positions
        elif price <= self.target_price and self.direction == -1:
            self.close_position(price)
        # check upper horizontal barrier for short positions
        elif price >= self.stop_price and self.direction == -1:
            self.close_position(price)
        # cehck special case of vertical barrier
        elif time == self.end_date:
            self.close_position(price)
        # check vertical barrier
        elif self.max_holding <= 0:
            self.close_position(price)
        # if all above conditions not true, decrement max holding by 1 and append a zero to returns column
        else:
            self.max_holding = self.max_holding - 1
            self.returns_series.append(0)


    def run_backtest(self):
        #signals generated from child class
        self.generate_signals()
        
        #loop over dataframe 
        for row in self.DGMT.df.itertuples():
            #if we get a long signal and do not have open position open a long
            if row.entry == 1 and self.open_pos is False:
                self.open_long(row.t_plus)
            #if we get a short position and do not have open position open a sort
            elif row.entry == -1 and self.open_pos is False:
                self.open_short(row.t_plus)
            #monitor open positions to see if any of the barriers have been touched, see function above
            elif self.open_pos:
                self.monitor_open_positions(row.close, row.Index)
            else:
                self.returns_series.append(0)
        self.DGMT.df['returns'] = self.returns_series
        self.returns_series = []