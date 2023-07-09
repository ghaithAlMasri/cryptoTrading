import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
class DGMT:
    def __init__(self, df_path, date_col) -> None:
        self.data = pd.read_csv(df_path, parse_dates=[date_col], index_col=date_col)
        self.data.drop('Unnamed: 0', inplace=True, axis=1)
        self.data['t_plus'] = self.data.open.shift(-1)
        self.data.dropna(inplace=True)
        self.timeframe = '1min'
        self.df = self.data.copy()

    def recreate_df(self, new_timeframe):
        agg_df = {'open': 'first',
                         'low': 'min', 'high': 'max',
                         'close': 'last',
                         'volume': 'sum', 't_plus': 'last'}

        self.df = self.data.resample(new_timeframe).agg(agg_df)
        self.timeframe = new_timeframe