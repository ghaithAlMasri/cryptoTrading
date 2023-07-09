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

    def __init__(self, csv_path, date_col, max_holding , ub_mult = 1.005, lb_mult = 0.995):

        self.dmgt = DGMT(csv_path, date_col)

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
        self.ub_mult = ub_mult
        self.lb_mult = lb_mult

        # special case of vertical barrier
        self.end_date = self.dmgt.df.index.values[-1]

        self.returns_series = []
        self.holding_series = []
        self.direction_series = []

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
        self.add_zeros()

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
        self.add_zeros()

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

    def add_zeros(self):
        self.returns_series.append(0)
        self.holding_series.append(0)
        self.direction_series.append(0)


    def close_position(self, price):
        '''

        :param price: price we are exiting trade at
        :return: appends the trade pnl to the returns series
        and resets variables
        '''
        pnl = (price / self.entry_price - 1) * self.direction
        self.process_close_var(pnl)
        self.reset_variables()

    def process_close_var(self, pnl):
        self.returns_series.append(pnl)
        self.direction_series.append(self.direction)
        holding = self.max_holding_limit - self.max_holding
        self.holding_series.append(holding)

    def generate_signals(self):
        '''

        use this function to make sure generate signals has been included in the child class
        '''
        if 'entry' not in self.dmgt.df.columns:
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
            self.add_zeros()

    def add_trade_cols(self):
        '''
        merges the new columns we created for our backtest into our dataframe,
        also resets the returns series to empty lists, incase we want to change the strategy heartbeat. 
        '''
        self.dmgt.df['returns'] = self.returns_series
        self.dmgt.df['holding'] = self.holding_series
        self.dmgt.df['direction'] = self.direction_series

        self.returns_series = []
        self.holding_series = []
        self.direction_series = []

    def run_backtest(self):
        # signals generated from child class
        self.generate_signals()

        # loop over dataframe
        for row in self.dmgt.df.itertuples():
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
                self.add_zeros()

        self.add_trade_cols()

    def show_performance(self):
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(f'total trades: {abs(self.dmgt.df.direction).sum()}')
        print(f'initial acc: $100')
        print(f'total pnl: {self.dmgt.df.returns.cumsum().values[-1]}')
        print(f'acc final: ${( (self.dmgt.df.returns.cumsum().values[-1] + 1)) * 100}')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        # plt.style.use('ggplot')
        # plt.figure()
        # plt.plot(self.dmgt.df.index, self.dmgt.df.returns.cumsum())
        # plt.show()
