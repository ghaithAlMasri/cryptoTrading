import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime as dt
from Clean_data import Cleandata
from pandas.plotting import register_matplotlib_converters



class visualize:

    def __init__(self,name) -> None:
        register_matplotlib_converters()
        plt.style.use('ggplot')
        self.df = Cleandata(f'/Users/ghaithalmasri/Desktop/fullstackroad/{name}.csv', 'BTCUSDT').retdf()
        self.df['time'] = pd.to_datetime(self.df['time'])


    def vis(self) -> None:
        plt.plot(self.df.time, self.df.close, c='blue')
        plt.title(f'Close x Time')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show()


trial = visualize('BTCUSDT').vis()


