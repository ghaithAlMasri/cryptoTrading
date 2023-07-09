from clean_data import cleandata
from datetime import datetime as dt
import pandas as pd
import numpy as np
import math
class weekday:
    def __init__(self) -> None:
        self.df = cleandata('/Users/ghaithalmasri/Desktop/fullstackroad/BTCUSDT.csv','BTCUSDT').retdf()
        self.df.time = pd.to_datetime(self.df.time)
        self.df['day'] = self.df.time.dt.weekday
        self.df['to_position'] = np.where((self.df.day >= 4) & (self.df.day <= 6), 1, -1)
        self.df.close = pd.to_numeric(self.df.close)
        self.df['logret'] = math.log((self.df.close/self.df.close.shift(1)),math.e)
        print(self.df.logret)



weekday()